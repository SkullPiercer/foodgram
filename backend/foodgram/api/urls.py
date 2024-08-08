from rest_framework.routers import SimpleRouter
from django.urls import include, path

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet, AvatarViewSet, SubscribeCreateView, FavoriteViewSet


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
    path('users/<int:id>/subscribe/', SubscribeCreateView.as_view(), name='subscribe_create'),
    path('recipes/<int:id>/favorite/', FavoriteViewSet.as_view(
        {
            'post': 'add_to_favorites',
            'delete': 'remove_from_favorites',
        }
    ), name='favorite_create_delete')
]
