from django.contrib import admin

from ingredients.models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка отображения ингредиентов в административной панели."""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_per_page = 50
    ordering = ('name',)
