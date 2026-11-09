from rest_framework.exceptions import ValidationError


class RelationActionMixin:
    """Класс по реализации следующей логики связи объекта с пользователем:
        добавление в избранное
        добавление в список продуктов
        подписка на автора.
    """

    through_model = type
    already_msg = ''
    absent_msg = ''

    def relation_queryset(self, obj):
        """Метод определения связи объекта с пользователем."""
        raise NotImplementedError

    def relation_kwargs(self, obj):
        """Метод возвращающий параметры для создания новой связи."""
        raise NotImplementedError

    def relation_serializer(self, obj):
        """Сериализатор."""
        raise NotImplementedError

    def add_relation(self, obj):
        """Проверка на наличие связи."""
        if self.relation_queryset(obj).exists():
            raise ValidationError({'detail': self.already_msg})
        self.through_model.objects.create(**self.relation_kwargs(obj))

    def remove_relation(self, obj):
        """Удаление связи."""
        deleted, _ = self.relation_queryset(obj).delete()
        if not deleted:
            raise ValidationError({'detail': self.absent_msg})
