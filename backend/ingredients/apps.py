from django.apps import AppConfig


class IngredientsConfig(AppConfig):
    """Конфигурация приложения со справочником ингредиентов."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ingredients'
    verbose_name = 'Интгредиенты'
