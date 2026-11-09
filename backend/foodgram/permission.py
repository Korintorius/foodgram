from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """Разрешает читать объект всем, а изменять и удалять только автору."""

    message = 'У вас недостаточно прав для выполнения данного действия.'

    def has_object_permission(self, request, view, obj):
        """Метод проверки прав на конкретный объект."""
        if request.method in SAFE_METHODS:
            return True
        return obj.author_id == request.user.pk
