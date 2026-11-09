import csv
import io

from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from foodgram.pagination import CustomPagination
from foodgram.permission import IsAuthorOrReadOnly
from recipes.constants import SHOPPING_LIST_FILENAME
from recipes.filters import RecipeFilter
from recipes.models import Favorite, IngredientInRecipe, Recipe, ShoppingCart
from recipes.serializers import (
    RecipeCreateSerializer,
    RecipeMinifiedSerializer,
    RecipeSerializer,
    RecipeUpdateSerializer
)


class RecipeViewSet(viewsets.ModelViewSet,):
    """API рецептов:
    - Создание, Изменение, Удаление (CRUD),
    - Фильтрация,
    - Избранное,
    - Список покупок,
    - Выгрузка."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = CustomPagination

    def get_queryset(self):
        """Возвращает рецепты с подгрузкой избранного и корзины."""
        return self._base_queryset().prefetch_related(
            'favorited',
            'in_shopping_cart',
        )

    def _base_queryset(self):
        """Базовый запрос с автором, тегами и ингредиентами."""
        return (
            Recipe.objects.select_related('author').
            prefetch_related('tags', 'ingredients_entries__ingredient').
            order_by('-created_at', '-id')
        )

    def get_serializer_class(self):
        """Выбор сериализатора под текущее действие."""
        return {
            'create': RecipeCreateSerializer,
            'update': RecipeUpdateSerializer,
            'partial_update': RecipeUpdateSerializer,
        }.get(self.action, RecipeSerializer)

    def perform_create(self, serializer):
        """Назначение текущего пользователя автором рецепта."""
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        """Создание рецепта."""
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)
        return Response(
            self._read_serializer(write_serializer.instance).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Обновление рецепта."""
        partial = kwargs.pop('partial', False)
        write_serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=partial
        )
        write_serializer.is_valid(raise_exception=True)
        write_serializer.save()
        return Response(
            self._read_serializer(write_serializer.instance).data,
            status=status.HTTP_200_OK
        )

    def _read_serializer(self, recipe):
        """Создание сериализатора чтения рецепта с контекстом."""
        return RecipeSerializer(recipe, context=self.get_serializer_context())

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт во фроненде."""
        recipe = self.get_object()
        return Response({
            'short-link': f'{settings.FRONTEND_URL}/recipes/{recipe.pk}'
        })

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта из избранного."""
        return self._toggle_relation(
            self.get_object(),
            request,
            through_model=Favorite,
            already_msg='Рецепт уже есть в избранном.',
            absent_msg='Рецепта нет в избранном.',
        )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта из списка покупок."""
        return self._toggle_relation(
            self.get_object(),
            request,
            through_model=ShoppingCart,
            already_msg='Рецепт уже есть в списке покупок.',
            absent_msg='Рецепта нет в списке покупок.',
        )

    def _toggle_relation(
            self,
            recipe,
            request,
            *,
            through_model,
            already_msg,
            absent_msg,):
        """Общая логика добавления/удаления связи с рецептом."""
        relation = through_model.objects.filter(
            user=request.user,
            recipe=recipe,
        )

        if request.method == 'POST':
            if relation.exists():
                raise ValidationError({'detail': already_msg})
            through_model.objects.create(user=request.user, recipe=recipe)
            return Response(
                RecipeMinifiedSerializer(
                    recipe,
                    context=self.get_serializer_context(),
                ).data,
                status=status.HTTP_201_CREATED,
            )
        deleted, _ = relation.delete()
        if not deleted:
            raise ValidationError({'detail': absent_msg})
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated],
            url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        """Выгрузка списка покупок пользователя в формат CSV."""
        entries = (
            IngredientInRecipe.objects
            .filter(recipe__in_cart__user=request.user)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(amount=Sum('amount'))
            .order_by(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
        )

        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator='\n')
        for entry in entries:
            writer.writerow([
                entry['ingredient__name'],
                entry['ingredient__measurement_unit'],
                entry['amount'],
            ])

        response = HttpResponse(
            '\ufeff' + buffer.getvalue(),
            content_type='text/csv; charset=utf-8',
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{SHOPPING_LIST_FILENAME}"'
        )
        return response

    def list(self, request, *args, **kwargs):
        """Возвращает рецепты с фильтрацией и пагинацией."""
        queryset = RecipeFilter(request=request).get_queryset(
            self.filter_queryset(self.get_queryset()))
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(RecipeSerializer(
                page, many=True, context=self.get_serializer_context()).data)
        return Response(RecipeSerializer(
            queryset, many=True, context=self.get_serializer_context()).data)
