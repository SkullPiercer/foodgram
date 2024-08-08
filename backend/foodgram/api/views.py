from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from rest_framework import viewsets, status, permissions, generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from .models import Ingredient, Recipe, Tag, Subscribe, Favorite
from .serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    TagSerializer,
    UserSerializer,
    SubscribeSerializer,
    FavoriteSerializer
)

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


class AvatarViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AvatarSerializer

    @action(detail=False, methods=('put',),
            permission_classes=[IsAuthenticated])
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

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SubscribeCreateView(generics.CreateAPIView):
    queryset = Subscribe.objects.all()
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        subscribed_to_id = self.kwargs.get('id')
        try:
            subscribed_to = User.objects.get(id=subscribed_to_id)
        except User.DoesNotExist:
            raise ValidationError("User does not exist.")

        serializer.save(subscriber=self.request.user,
                        subscribed_to=subscribed_to)


class FavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Favorite.objects.all()

    @action(detail=False, methods=('post',))
    def add_to_favorites(self, request, id):
        user = request.user
        serializer = FavoriteSerializer(data={}, context={'request': request, 'view': self})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
