class RecipeMixin:
    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request', None)
        if request is None or not request.user.is_authenticated:
            return False
        return obj.shop_recipe.filter(user=request.user).exists()

    def get_is_favorited(self, obj):
        request = self.context.get('request', None)
        if request is None or not request.user.is_authenticated:
            return False
        return obj.favorited_by.filter(recipe=obj, user=request.user).exists()
