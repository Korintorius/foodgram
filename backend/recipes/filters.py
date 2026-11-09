

class RecipeFilter:
    """Фильтр рецептов по тегам, автору, избранному и списку покупок."""

    def __init__(self, request):
        """Инициализация запросов с параметрами фильтрации."""
        self.request = request

    def get_queryset(self, queryset):
        """Применение фильтров из параметров к списку рецептов."""
        params = self.request.query_params

        tags = params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags)

        author = params.get('author')
        if author:
            try:
                author_id = int(author)
            except (TypeError, ValueError):
                return queryset.none()
            queryset = queryset.filter(author_id=author_id)

        queryset = self._apply_flag(queryset, params.get('is_favorited'),
                                    'favorited',)
        queryset = self._apply_flag(queryset,
                                    params.get('is_in_shopping_cart'),
                                    'in_shopping_cart',)
        return queryset.distinct()

    def _apply_flag(self, queryset, raw_value, m2m_field):
        """Фильтрация по флагу 0/1 для избранного и списка покупок."""
        if raw_value not in ('0', '1'):
            return queryset

        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if raw_value == '1' else queryset

        lookup = {f'{m2m_field}__pk': user.pk}
        if raw_value == '1':
            return queryset.filter(**lookup)
        return queryset.exclude(**lookup)
