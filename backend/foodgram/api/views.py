from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser import views as djoser_views
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientsFilter, RecipeFilter
from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShopList,
    Tag,
)
from .permissions import Author
from .serializers import (
    AvatarSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    ShopListSerializer,
    ShortURLSerializer,
    SubscribeCreateSerializer,
    SubscribeListSerializer,
    TagSerializer,
    UserSerializer,
)


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter


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

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        data = User.objects.filter(subscribed_to__subscriber=self.request.user)
        page = self.paginate_queryset(data)
        serializer = SubscribeListSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        user = request.user
        subscribed_to = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            data = {'subscriber': user.id, 'subscribed_to': id}
            serializer = SubscribeCreateSerializer(
                data=data,
                context={'request': request, 'view': self}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = user.subscriber.filter(subscribed_to=subscribed_to)
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class AvatarViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AvatarSerializer

    @action(detail=False, methods=('put',),
            permission_classes=(IsAuthenticated,))
    def update_avatar(self, request):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data,
                                      partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=('delete',),
            permission_classes=(IsAuthenticated,))
    def delete_avatar(self, request):
        user = request.user
        user.avatar.delete(save=False)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (Author, permissions.IsAuthenticatedOrReadOnly)
    pagination_class = PageNumberPagination
    PageNumberPagination.page_size_query_param = 'limit'
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=('get',))
    def download_shopping_cart(self, request):
        user = request.user
        file_name = f'{user.username}_shopping_list.txt'
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file_name}'

        shop_list = user.shop_user.all()

        file_data = {
            'Ваш список покупок': '\n\n',
        }
        ingredients_summary = {}
        for item in shop_list:
            recipe_ingredients = RecipeIngredients.objects.filter(
                recipe=item.recipe
            )
            for recipe_ingredient in recipe_ingredients:
                ingredient_name = recipe_ingredient.ingredient.name
                quantity = recipe_ingredient.amount

                if ingredient_name in ingredients_summary:
                    ingredients_summary[ingredient_name] += quantity
                else:
                    ingredients_summary[ingredient_name] = quantity

        for ingredient, total_quantity in ingredients_summary.items():
            meas_unit = recipe_ingredient.ingredient.measurement_unit.title
            file_data[
                f"{ingredient} ({meas_unit})"] = f"{total_quantity}\n"

        response.write("\n".join(f"{k}: {v}" for k, v in file_data.items()))

        return response


class FavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Favorite.objects.all()

    @action(detail=False, methods=('post',))
    def add_to_favorites(self, request, id):
        serializer = FavoriteSerializer(
            data={},
            context={'request': request, 'view': self}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=('delete',))
    def remove_from_favorites(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        try:
            favorite = user.favorites.get(recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response(
                {'detail': 'Favorite not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ShopViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ShopList.objects.all()

    @action(detail=False, methods=('post',))
    def add_to_shop_list(self, request, id):
        serializer = ShopListSerializer(
            data={},
            context={'request': request, 'view': self}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=('delete',))
    def remove_from_shop_list(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        try:
            shop = user.shop_user.get(recipe=recipe)
            shop.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShopList.DoesNotExist:
            return Response(
                {'detail': 'Recipe not in shop list.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class RecipeShortURL(generics.RetrieveAPIView):
    queryset = Recipe.objects.all()
    serializer_class = ShortURLSerializer
    lookup_field = 'id'
