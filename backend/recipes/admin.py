from django.contrib import admin

from recipes.models import Favorite, IngredientInRecipe, Recipe, ShoppingCart


class IngredientInRecipeInline(admin.TabularInline):
    """Встроенный список ингредиентов в карточке рецепта."""

    model = IngredientInRecipe
    extra = 1
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка отображения рецептов в админ-панели."""

    list_display = ('id', 'name', 'author', 'favorites_count', 'created_at')
    list_filter = ('tags', 'created_at')
    search_fields = (
        'name',
        'author__username',
        'author__email',
        'author__first_name',
        'author__last_name',
    )

    filter_horizontal = ('tags',)
    readonly_fields = ('favorites_count',)
    inlines = (IngredientInRecipeInline,)
    autocomplete_fields = ('author',)
    list_per_page = 25

    @admin.display(description='Добавление в избранное')
    def favorites_count(self, obj):
        """Метод возвращает количество добавлений рецепта в избранное."""
        return obj.favorite_by.count()


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Список связей рецепта и ингредиентов."""

    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    autocomplete_fields = ('recipe', 'ingredient')
    list_per_page = 50


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Список избранных рецептов пользователей."""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__email', 'user__username', 'recipe__name')
    autocomplete_fields = ('user', 'recipe')
    list_per_page = 50


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Список покупок пользователей."""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__email', 'user__username', 'recipe__name')
    autocomplete_fields = ('user', 'recipe')
    list_per_page = 50
