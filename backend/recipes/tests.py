from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from ingredients.models import Ingredient
from recipes.models import IngredientInRecipe, Recipe


class RecipeListOrderingTest(APITestCase):
    """Тесты списка рецептов:
    - Сортировка
    - Пагинация
    - Состав рецепта."""

    def setUp(self):
        """Создание тестового пользователя и 8 рецептов с разными датами."""
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123',
        )
        base = timezone.now()
        self.recipes = []
        for i in range(8):
            recipe = Recipe.objects.create(
                author=self.user,
                name=f'Рецепт {i}',
                image='recipes/images/test.jpg',
                text='Описание',
                cooking_time=10,
            )
            Recipe.objects.filter(pk=recipe.pk).update(
                created_at=base + timedelta(minutes=i)
            )
            self.recipes.append(recipe)

    def _expected_ids(self):
        """Возвращение идентификаторов рецептов в порядке выдачи."""
        return list(
            Recipe.objects
            .order_by('-created_at', '-id')
            .values_list('id', flat=True)
        )

    def test_first_page_returns_six_newest(self):
        """Проверка, что первая страница содержит 6 самых новых рецептов."""
        response = self.client.get('/api/recipes/?page=1&limit=6')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 8)
        self.assertEqual(len(response.data['results']), 6)
        self.assertEqual(
            [item['id'] for item in response.data['results']],
            self._expected_ids()[:6],
        )

    def test_second_page_returns_remaining(self):
        """Проверка, что вторая станица содержит оставшиеся рецепты."""
        response = self.client.get('/api/recipes/?page=2&limit=6')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(
            [item['id'] for item in response.data['results']],
            self._expected_ids()[6:],
        )

    def test_default_page_size_is_six(self):
        """Проверка размера страницы. По умолчанию - 6 рецептов."""
        response = self.client.get('/api/recipes/?page=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 6)

    def test_recipe_payload_contains_ingredients(self):
        """Проверка наличия состава ингредиентов в ответе API."""
        ingredient = Ingredient.objects.create(
            name='Мука',
            measurement_unit='г',
        )
        IngredientInRecipe.objects.create(
            recipe=self.recipes[-1],
            ingredient=ingredient,
            amount=100,
        )

        response = self.client.get('/api/recipes/?page=1&limit=6')

        self.assertEqual(response.status_code, 200)
        item = next(
            recipe for recipe in response.data['results']
            if recipe['id'] == self.recipes[-1].id
        )
        self.assertIn('ingredients', item)
        self.assertEqual(
            item['ingredients'],
            [{
                'id': ingredient.id,
                'name': 'Мука',
                'measurement_unit': 'г',
                'amount': 100,
            }],
        )
