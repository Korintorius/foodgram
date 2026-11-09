

class IngredientFilter:
    """Реализация фильтрации ингредиентов."""

    def __init__(self, request):
        """Метод инициализации."""
        self.request = request

    def get_queryset(self, queryset):
        """Метод определения набора данных."""
        name = (self.request.query_params.get('name') or '').strip()
        if not name:
            return queryset

        return queryset.filter(name__istartswith=name).order_by('name')
