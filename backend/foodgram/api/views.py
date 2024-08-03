from django.contrib.auth import get_user_model
from djoser import views as djoser_views
from rest_framework import viewsets, status, permissions


from .models import Ingredient, Tag
from .serializers import IngredientSerializer, TagSerializer, UserSerializer

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
