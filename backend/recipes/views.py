from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from foodgram.pagination import CustomPageNumberPaginator
from recipes.filters import IngredientsFilter, RecipeFilter
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingList, Tag
)
from recipes.mixins import RetriveAndListViewSet
from recipes.permissions import IsAuthorOrAdminOrReadOnly
from recipes.serializers import (
    AddRecipeSerializer, FavouriteSerializer, IngredientsSerializer,
    ShoppingListSerializer, ShowRecipeFullSerializer, TagsSerializer,
)
from recipes.utils import download_response, get_ingredients_list


class IngredientsViewSet(RetriveAndListViewSet):
    queryset = Ingredient.objects.all().order_by('id')
    serializer_class = IngredientsSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientsFilter
    pagination_class = None


class TagsViewSet(RetriveAndListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPaginator

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ShowRecipeFullSerializer
        return AddRecipeSerializer

    @action(detail=True, permission_classes=[IsAuthorOrAdminOrReadOnly])
    def favorite(self, request, pk):
        """Кастомный метод обработки эндпоинта ./favorite/."""
        data = {'user': request.user.id, 'recipe': pk}
        serializer = FavouriteSerializer(
            data=data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            Favorite.objects.get(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response(
                'Данный рецепт уже отсутствует в избранном.',
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, permission_classes=[IsAuthorOrAdminOrReadOnly])
    def shopping_cart(self, request, pk):
        """Кастомный метод обработки эндпоинта ./shopping_cart/."""
        data = {'user': request.user.id, 'recipe': pk}
        serializer = ShoppingListSerializer(
            data=data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        bad_request = Response(
            'Данный рецепт уже отсутствует в списке покупок.',
            status=status.HTTP_400_BAD_REQUEST,
        )
        try:
            try:
                recipe = Recipe.objects.get(id=pk)
            except Recipe.DoesNotExist:
                return bad_request
            shopping_list = ShoppingList.objects.get(
                user=request.user,
                recipe=recipe,
            )
            shopping_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShoppingList.DoesNotExist:
            return bad_request

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        """Кастомный метод обработки эндпоинта ./download_shopping_cart/."""
        ingredients_list = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        )
        list_to_buy = get_ingredients_list(ingredients_list)
        return download_response(list_to_buy, 'Список покупок.txt')
