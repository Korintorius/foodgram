from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminUserCreationForm
from django.utils.translation import gettext_lazy as _

from users.models import Subscription

User = get_user_model()


class UserCreationForm(AdminUserCreationForm):
    """Форма создания пользователя в админке при входе по email."""

    class Meta(AdminUserCreationForm.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')
        field_classes = {
            'username': AdminUserCreationForm.Meta.field_classes['username']}


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Настройка отображения и редактирования подьзователей в админке."""

    add_form = UserCreationForm

    list_display = ('id', 'email', 'username', 'first_name',
                    'last_name', 'is_staff')
    search_fields = ('email', 'username')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('id',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': (
            'username', 'first_name', 'last_name')}),
        (_('Permissions'), {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups',
            'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Аватар'), {'fields': ('avatar',)}),
    )

    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': (
            'email', 'username', 'first_name', 'last_name',
            'usable_password', 'password1', 'password2')})
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройка списка подписок в админке."""

    list_display = ('id', 'subscriber', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('subscriber__email', 'subscriber__username',
                     'author__email', 'author__username')
    autocomplete_fields = ('subscriber', 'author')
