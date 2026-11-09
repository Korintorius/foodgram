from django.contrib import admin

from tags.models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка отображения тегов в административной панели."""
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    list_per_page = 25
    ordering = ('name',)
