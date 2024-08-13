from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from rest_framework import viewsets, status, permissions, generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from .models import Ingredient, Recipe, Tag, Subscribe, Favorite, ShopList
from .serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    TagSerializer,
    UserSerializer,
    SubscribeCreateSerializer,
    FavoriteSerializer,
    ShopListSerializer,
    ShortURLSerializer
)
from .permissions import Author

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        user = self.request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=('post',),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        user = request.user
        data = {'subscriber': user.id, 'subscribed_to': id}
        serializer = SubscribeCreateSerializer(data=data, context={'request': request, 'view': self})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvatarViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AvatarSerializer

    @action(detail=False, methods=('put',),
            permission_classes=(IsAuthenticated,))
    def update_avatar(self, request):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data,
                                      partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=('delete',),
            permission_classes=[IsAuthenticated])
    def delete_avatar(self, request):
        user = request.user
        user.avatar.delete(save=False)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (Author, permissions.IsAuthenticatedOrReadOnly)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author',)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Favorite.objects.all()

    @action(detail=False, methods=('post',))
    def add_to_favorites(self, request, id):
        serializer = FavoriteSerializer(data={}, context={'request': request,
                                                          'view': self})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=('delete',))
    def remove_from_favorites(self, request, id):
        user = request.user
        try:
            recipe = get_object_or_404(Recipe, id=id)
            favorite = Favorite.objects.get(user=user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response({'detail': 'Favorite not found.'},
                            status=status.HTTP_400_BAD_REQUEST)


class ShopViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ShopList.objects.all()

    @action(detail=False, methods=('post',))
    def add_to_shop_list(self, request, id):
        serializer = ShopListSerializer(data={}, context={'request': request,
                                                          'view': self})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=('delete',))
    def remove_from_shop_list(self, request, id):
        user = request.user
        try:
            recipe = get_object_or_404(Recipe, id=id)
            shop = ShopList.objects.get(user=user, recipe=recipe)
            shop.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShopList.DoesNotExist:
            return Response({'detail': 'Recipe not in shop list.'},
                            status=status.HTTP_400_BAD_REQUEST)


class RecipeShortURL(generics.RetrieveAPIView):
    queryset = Recipe.objects.all()
    serializer_class = ShortURLSerializer
    lookup_field = 'id'
