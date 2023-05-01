import django_filters as filters

from recipes.models import Ingredient, Recipe


class RecipeFilter(filters.FilterSet):
    """Класс фильтрации рецептов."""

    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr="iexact",
        label='Tags',
    )
    is_favorited = filters.BooleanFilter(
        method='get_favorite',
        label='Favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shopping',
        label='Is in shopping list',
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'author',
            'tags',
            'is_in_shopping_cart',
        )

    def get_favorite(self, queryset, name, item_value):
        """Метод получения рецептов в избранном."""

        if item_value:
            return Recipe.objects.filter(in_favorite__user=self.request.user)
        return Recipe.objects.all()

    def get_shopping(self, queryset, name, item_value):
        """Метод получения рецептов в списке покупок."""

        if item_value and not self.request.user.is_anonymous:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientsFilter(filters.FilterSet):
    """Класс фильтрации ингредиентов."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
