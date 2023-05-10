from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientsFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AddRecipeSerializer,
    IngredientsSerializer,
    RecipeSerializer,
    ShowRecipeFullSerializer,
    TagsSerializer,
)
from foodgram.pagination import CustomPageNumberPaginator
from recipes.mixins import RetriveAndListViewSet
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag,
)
from recipes.utils import download_response, get_ingredients_list


class IngredientsViewSet(RetriveAndListViewSet):
    """Ингредиенты."""

    queryset = Ingredient.objects.all().order_by('id')
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientsFilter
    serializer_class = IngredientsSerializer
    pagination_class = None


class TagsViewSet(RetriveAndListViewSet):
    """Теги."""

    queryset = Tag.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = TagsSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""

    queryset = Recipe.objects.all().order_by('-id')
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPaginator

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ShowRecipeFullSerializer
        return AddRecipeSerializer

    def add_obj(self, model, user, id):
        """Функция добавления нового объекта выбранной модели."""
        if model.objects.filter(user=user, recipe__id=id).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe = get_object_or_404(Recipe, id=id)
        model.objects.create(user=user, recipe=recipe)
        serialized_obj = RecipeSerializer(recipe)
        return Response(serialized_obj.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, user, id):
        """Функция удаления выбранного объекта модели."""
        recipe = model.objects.filter(user=user, recipe__id=id)
        if recipe.exists():
            recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт уже удален!'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthorOrReadOnly],
    )
    def favorite(self, request, pk):
        """Метод обработки эндпоинта /favorite/."""
        if request.method == 'POST':
            return self.add_obj(
                model=Favorite,
                user=request.user,
                id=pk,
            )
        else:
            return self.delete_obj(
                model=Favorite,
                user=request.user,
                id=pk,
            )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthorOrReadOnly],
    )
    def shopping_cart(self, request, pk):
        """Метод обработки эндпоинта /shopping_cart/."""
        if request.method == 'POST':
            return self.add_obj(
                model=ShoppingList,
                user=request.user,
                id=pk,
            )
        else:
            return self.delete_obj(
                model=ShoppingList,
                user=request.user,
                id=pk,
            )

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        """Метод скачивания списка покупок ./download_shopping_cart/."""
        ingredients_list = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        )
        list_to_buy = get_ingredients_list(ingredients_list)
        return download_response(list_to_buy, 'Список покупок.txt')
