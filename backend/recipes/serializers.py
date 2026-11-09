from django.db import transaction
from rest_framework import serializers

from foodgram.fields import Base64ImageField
from ingredients.models import Ingredient
from recipes.constants import REQUIRED_ON_UPDATE
from recipes.models import IngredientInRecipe, Recipe
from tags.models import Tag
from tags.serializers import TagSerializer
from users.serializers import UserSerializer


class IngredientAmountSerializer(serializers.Serializer):
    """Ингредиент и его количество во входных данных рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(min_value=1)

    def to_representation(self, instance):
        """Возвращает идентификатор ингредиента и его количество."""
        return {'id': instance.ingredient_id, 'amount': instance.amount}


class RecipeWriteSerializerMixin:
    """Общая логика проверки и сохранения рецепта."""

    required_fields: tuple[str, ...] = ()

    def validate(self, attrs):
        """Проверяет обязательные поля, теги и ингредиенты."""
        missing = [field for field in self.required_fields
                   if field not in attrs]
        if missing:
            raise serializers.ValidationError({
                field: ['Это поле обязательно.'] for field in missing
            })

        tags = attrs.get('tags')
        if 'tags' in attrs:
            if not tags:
                raise serializers.ValidationError({
                    'tags': ['Укажите хотя бы один тег.'],
                })
            if len(tags) != len(set(tags)):
                raise serializers.ValidationError({
                    'tags': ['Теги не должны повторяться.'],
                })

        ingredients = attrs.get('ingredients')
        if 'ingredients' in attrs:
            if not ingredients:
                raise serializers.ValidationError({
                    'ingredients': ['Укажите хотя бы один ингредиент.'],
                })
            ids = [item['id'].pk for item in ingredients]
            if len(ids) != len(set(ids)):
                raise serializers.ValidationError({
                    'ingredients': ['Ингредиенты не должны повторяться.'],
                })
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Создает рецепт вместе с тегами и составов."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount'])
            for item in ingredients
        ])
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет рецепт, картинку, теги и состав."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        old_image = instance.image if instance.image else None

        recipe = super().update(instance, validated_data)

        if old_image and recipe.image and old_image.name != recipe.image.name:
            old_image.delete(save=False)

        if tags is not None:
            recipe.tags.set(tags)
        if ingredients is not None:
            recipe.ingredients_entries.all().delete()
            IngredientInRecipe.objects.bulk_create([
                IngredientInRecipe(recipe=recipe, ingredient=item['id'],
                                   amount=item['amount'])
                for item in ingredients
            ])
        return recipe


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Ингредиент в составе рецепта для ответа по API."""

    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Полное представление рецепта ддля чтения."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredients_entries', many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

        read_only_fields = fields

    def get_is_favorited(self, recipe):
        """Показывает, есть ли рецепт в избранном пользователя."""
        return self._user_in_relation(recipe.favorited.all())

    def get_is_in_shopping_cart(self, recipe):
        """Показывает, есть ли рецепт в списке покупок пользователя."""
        return self._user_in_relation(recipe.in_shopping_cart.all())

    def _user_in_relation(self, related_users):
        """Проверяет наличие текущего пользователя в списке связей."""
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return False
        return any(item.pk == user.pk for item in related_users)


class RecipeCreateSerializer(RecipeWriteSerializerMixin, serializers.
                             ModelSerializer):
    """Создание рецепта: Post/api/recipes/."""

    image = Base64ImageField(required=True)
    name = serializers.CharField(max_length=256, required=True)
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(min_value=1, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True,
    )
    ingredients = IngredientAmountSerializer(many=True, required=True)

    class Meta:
        model = Recipe
        fields = ('image', 'name', 'text', 'cooking_time', 'tags',
                  'ingredients')


class RecipeUpdateSerializer(RecipeCreateSerializer):
    """Обновление рецепта: PATCH/api/recipes/{id}."""

    image = Base64ImageField(required=False)
    required_fields = REQUIRED_ON_UPDATE


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Короткое представление рецепта для избранного и списка покупок."""

    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields
