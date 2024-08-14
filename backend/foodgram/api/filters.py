from django_filters import rest_framework as filters

from .models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ['author', 'is_favorited']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorites__user=user)
        return queryset
