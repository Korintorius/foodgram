from rest_framework.viewsets import ReadOnlyModelViewSet

from ingredients.filters import IngredientFilter
from ingredients.models import Ingredient
from ingredients.serializers import IngredientSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    """Класс для API интгредиентов:
        Просмотр списка,
        Просмотр одного элемента,
        Поиск по названи.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    lookup_field = 'pk'

    def get_queryset(self):
        """Метод, возвращающий ингредиенты с учетом поиска по названию."""
        queryset = super().get_queryset()
        return IngredientFilter(request=self.request).get_queryset(queryset)
