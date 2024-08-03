from rest_framework.routers import SimpleRouter
from django.urls import include, path

from .views import IngredientViewSet, TagViewSet, UserViewSet


router = SimpleRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
