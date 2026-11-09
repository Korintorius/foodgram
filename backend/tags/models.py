from django.db import models


class Tag(models.Model):
    """Модель тега рецепта:
    - название тега
    - slug для URL."""

    name = models.CharField(
        'название',
        max_length=32,
        unique=True,
        db_index=True
    )
    slug = models.SlugField(
        'слаг',
        max_length=32,
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ('name',)

    def __str__(self):
        """Возвращает название тега."""
        return self.name
