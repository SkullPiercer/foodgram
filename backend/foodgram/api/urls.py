from rest_framework.routers import SimpleRouter
from django.urls import include, path, re_path


from django_short_url import views as surl_views

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet, AvatarViewSet, FavoriteViewSet, ShopViewSet, RecipeShortURL


router = SimpleRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', UserViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', AvatarViewSet.as_view(
        {
            'put': 'update_avatar',
            'delete': 'delete_avatar',
        }
    )),
    path('recipes/<int:id>/favorite/', FavoriteViewSet.as_view(
        {
            'post': 'add_to_favorites',
            'delete': 'remove_from_favorites',
        }
    ), name='favorite_create_delete'),

    path('recipes/<int:id>/shopping_cart/', ShopViewSet.as_view(
        {
            'post': 'add_to_shop_list',
            'delete': 'remove_from_shop_list',
        }
    ), name='shop_list_create_delete'),
    path('recipes/<int:id>/get-link/', RecipeShortURL.as_view(), name='shor_url'),

]
