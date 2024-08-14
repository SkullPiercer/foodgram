from .models import Favorite, ShopList


class RecipeMixin:
    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request', None)
        if request is None or not request.user.is_authenticated:
            return False
        return ShopList.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()

    def get_is_favorited(self, obj):
        request = self.context.get('request', None)
        if request is None or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()
