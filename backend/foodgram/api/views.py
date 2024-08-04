from django.contrib.auth import get_user_model
from djoser import views as djoser_views
from rest_framework import viewsets, status, permissions
from rest_framework.pagination import LimitOffsetPagination

from .models import Ingredient, Tag
from .serializers import IngredientSerializer, TagSerializer, UserSerializer

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
