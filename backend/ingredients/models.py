from django.db import models


class Ingredient(models.Model):
    """Модель сущности ингредиент
        Название
        Единица измерения.
    """

    name = models.CharField(
        'Название',
        max_length=128,
        db_index=True
    )
    measurement_unit = models.CharField(
        'единица измерения',
        max_length=64
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ('name',)
