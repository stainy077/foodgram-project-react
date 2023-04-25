from django.conf import settings
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.response import Response

from recipes.models import Recipe
from users.models import Follow

User = get_user_model()


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор регистрации пользователя."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""


    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta():
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=self.context['request'].user,
            author=obj,
        ).exists()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        try:
            user = self.context.get('request').user
        except User.DoesNotExist:
            return Response(
                'Такого пользователя не существует!.',
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = self.context.get('request').user
        author_id = data['author'].id
        if Follow.objects.filter(user=user, author__id=author_id).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора!',
            )
        if user.id == author_id:
            raise serializers.ValidationError('Нельзя подписаться на себя!')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShowFollowersSerializer(
            instance.author,
            context={'request': request},
        ).data


class FollowingRecipesSerializers(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShowFollowersSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.follower.filter(user=obj, author=request.user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()[:(int(settings.RECIPES_LIMIT))]
        return FollowingRecipesSerializers(
            recipes,
            many=True,
            context={'request': request},
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
