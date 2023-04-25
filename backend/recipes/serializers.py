from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
    SlugRelatedField,
    ValidationError,
)

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag,
)
from users.serializers import CustomUserSerializer

User = get_user_model()


class IngredientsSerializer(ModelSerializer):
    """Сериализатор полей модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagsSerializer(ModelSerializer):
    """Сериализатор полей модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class ShowRecipeIngredientsSerializer(ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""

    id = PrimaryKeyRelatedField(
        read_only=True,
        source='ingredient'
    )
    name = SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='name'
    )
    measurement_unit = SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ShowRecipeSerializer(ModelSerializer):
    """Сериализатор уникальных полей модели Recipe."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShowRecipeFullSerializer(ModelSerializer):
    """Сериализатор параметров рецепта."""

    tags = TagsSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return ShowRecipeIngredientsSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            recipe=obj,
            user=request.user,
        ).exists()


class AddRecipeIngredientsSerializer(ModelSerializer):
    """Сериализатор, связывающий количество ингредиентов с ингредиентом."""

    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class AddRecipeSerializer(ModelSerializer):
    """Сериализатор, создающий новый рецепт."""

    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = AddRecipeIngredientsSerializer(many=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError('Не выбрано ни одного ингредиента!')
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise ValidationError('Количество должно быть положительным!')
        return data

    def validate_cooking_time(self, data):
        if data <= 0:
            raise ValidationError('Время готовки должно быть положительным'
                                  'числом, не менее 1 минуты!')
        return data

    def add_recipe_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if RecipeIngredient.objects.filter(
                recipe=recipe,
                ingredient=ingredient_id,
            ).exists():
                amount += ingredient['amount']
            RecipeIngredient.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient_id,
                defaults={'amount': amount},
            )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.add_recipe_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, recipe, validated_data):
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients.clear()
            self.add_recipe_ingredients(ingredients, recipe)
        if 'tags' in self.initial_data:
            tags_data = validated_data.pop('tags')
            recipe.tags.set(tags_data)
        super().update(recipe, validated_data)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        return ShowRecipeSerializer(
            recipe,
            context={'request': self.context.get('request')},
        ).data


class FavouriteSerializer(ModelSerializer):
    """Сериализатор, добавляющий рецепт в избранное."""

    recipe = PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if Favorite.objects.filter(user=user, recipe__id=recipe_id).exists():
            raise ValidationError('Рецепт уже добавлен в избранное!')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowRecipeSerializer(instance.recipe, context=context).data


class ShoppingListSerializer(ModelSerializer):
    """Сериализатор, создающий список покупок."""

    recipe = PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if ShoppingList.objects.filter(
            user=user,
            recipe__id=recipe_id,
        ).exists():
            raise ValidationError('Рецепт уже добавлен в список покупок!')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowRecipeSerializer(instance.recipe, context=context).data
