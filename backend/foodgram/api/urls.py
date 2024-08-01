from rest_framework.routers import SimpleRouter
from django.urls import include, path

from .views import TagViewSet


router = SimpleRouter()
router.register('tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]