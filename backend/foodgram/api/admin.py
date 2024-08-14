from django.contrib import admin
from django.db.models import Count

from .models import (
    CustomUser,
    Ingredient,
    Recipe,
    Subscribe,
    Tag,
    Unit,
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ('username', 'email')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(favorite_count=Count('favorited_by'))
        return queryset

    def favorite_count(self, obj):
        return obj.favorite_count

    favorite_count.short_description = 'Добавлен в избранное (раз)'

    list_display = ('name', 'author', 'favorite_count')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(Unit)
admin.site.register(Tag)
admin.site.register(Subscribe)
