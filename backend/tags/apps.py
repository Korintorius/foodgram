from django.apps import AppConfig


class TagsConfig(AppConfig):
    """Конфигурация приложения со справочником тегов."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tags'
    verbose_name = 'Теги'
