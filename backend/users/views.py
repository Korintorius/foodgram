from django.contrib.auth import get_user_model
from django.db.models import Count
from djoser.constants import Messages
from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from foodgram.mixins import RelationActionMixin
from foodgram.pagination import CustomPagination
from users.constants import AUTHENTICATED_ACTIONS
from users.models import Subscription
from users.serializers import (
    AvatarResponseSerializer,
    AvatarSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserWithRecipesSerializer
)

User = get_user_model()


class SubscriptionRelationMixin(RelationActionMixin):
    """Реализация связи Подписка:
    - Запрос,
    - Данные,
    - Ответ."""

    through_model = Subscription
    already_msg = 'Вы уже подписаны на этого пользователя'
    absent_msg = 'Вы не подписаны на этого пользователя'

    def relation_queryset(self, obj):
        """Возвращает подписку текущего пользователя на автора."""
        return Subscription.objects.filter(
            subscriber=self.request.user,
            author=obj
        )

    def relation_kwargs(self, obj):
        """Возвращает данные для создания подписки."""
        return {'subscriber': self.request.user, 'author': obj}

    def relation_serializer(self, obj):
        """Возвращает автора с рецептами для ответа."""
        return UserWithRecipesSerializer(
            obj, context=self.get_serializer_context()).data


class UserViewSet(
    SubscriptionRelationMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """Пользователи: список, профиль, регистрация, аватар, пароль, подписки."""

    queryset = None
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Возвращает пользователей или список подписок."""
        if self.action == 'subscriptions':
            subscribed_ids = Subscription.objects.filter(
                subscriber=self.request.user,
            ).values('author_id')
            return (
                User.objects.filter(pk__in=subscribed_ids)
                .annotate(recipes_count=Count('recipes', distinct=True))
                .order_by('id')
            )
        return User.objects.all().order_by('id')

    def get_permissions(self):
        """Требует авторизацию для закрытых действий."""
        if self.action in AUTHENTICATED_ACTIONS:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        """Выбор сериализатора под текущее действие."""
        return {
            'create': UserCreateSerializer,
            'me': UserSerializer,
            'avatar': AvatarSerializer,
            'set_password': SetPasswordSerializer,
            'subscriptions': UserWithRecipesSerializer,
            'subscribe': UserWithRecipesSerializer,
        }.get(self.action, UserSerializer)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """Возвращение профиля текущего пользователя."""
        return Response(self.get_serializer(request.user).data)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        """Загрузка, замена и удадения аватара пользователя."""
        user = request.user
        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=False)
                user.avatar = None
                user.save(update_fields=['avatar'])
            return Response(status=status.HTTP_204_NO_CONTENT)

        old_avatar = user.avatar
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if old_avatar and old_avatar.name != user.avatar.name:
            old_avatar.delete(save=False)

        return Response(
            AvatarResponseSerializer(
                user,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='set_password')
    def set_password(self, request):
        """Смена пароля текущего пользователя."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Инициация отправки письма для сброса пароля."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': Messages.EMAIL_SENT},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        """Возврат подписок пользователя с пагинацией."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        """Реализация подписывания на автора или отписывания от него."""
        target = self.get_object()
        if request.method == 'POST':
            if target.pk == request.user.pk:
                raise ValidationError(
                    {'detail': 'Нельзя подписать на самого себя'}
                )
            self.add_relation(target)
            return Response(
                self.relation_serializer(target),
                status=status.HTTP_201_CREATED,
            )
        self.remove_relation(target)
        return Response(status=status.HTTP_204_NO_CONTENT)
