from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from ingredients.models import Ingredient
from tags.models import Tag


class Recipe(models.Model):
    """Модель рецепта:
       - Автор,
       - Описание,
       - Картинка,
       - Время,
       - Теги,
       - Ингредиенты."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор публикации',
    )
    name = models.CharField(
        'название',
        max_length=256
    )
    image = models.ImageField(
        'картинка',
        upload_to='recipes/images/',
        blank=False
    )
    text = models.TextField(
        'текстовое описание'
    )
    cooking_time = models.PositiveIntegerField(
        'время приготовления в минутах',
        validators=[MinValueValidator(1)],
    )
    created_at = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='in_recipes',
        verbose_name='ингредиенты',
    )
    favorited = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Favorite',
        related_name='favorite_recipes',
        verbose_name='в избранном у',
    )
    in_shopping_cart = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ShoppingCart',
        related_name='shopping_cart_recipes',
        verbose_name='в списке покупок у',
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('-created_at', '-id')

    def __str__(self):
        """Возвращение название рецепта."""
        return self.name


class IngredientInRecipe(models.Model):
    """Модель ингредиента в рецепте:
    - Ссылка на ингредиент,
    - Количество ингредиента."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_entries',
        verbose_name='рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_entries',
        verbose_name='ингредиент',
    )
    amount = models.PositiveIntegerField(
        'количество',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='recipe_ingredient_unique',
                condition=models.Q(ingredient__isnull=False),
                violation_error_message='''Этот ингредиент уже
                добавлен в рецепт.''',
            ),
        ]
        ordering = ('id',)


class Favorite(models.Model):
    """Модель связи пользователя с избранным рецептом."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_by',
        verbose_name='рецепт',
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite_unique',
                condition=models.Q(user__isnull=False, recipe__isnull=False),
                violation_error_message='Рецепт уже есть в избранном',
            ),
        ]
        ordering = ('id',)


class ShoppingCart(models.Model):
    """Модели связи пользователя с рецептом в списке покупок."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_cart',
        verbose_name='рецепт'
    )

    class Meta:
        verbose_name = 'запись списка покупок'
        verbose_name_plural = 'списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping_cart_unique',
                condition=models.Q(user__isnull=False, recipe__isnull=False),
                violation_error_message='Рецепт уже есть в списке покупок.',
            ),
        ]
        ordering = ('id',)
