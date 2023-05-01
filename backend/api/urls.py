from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework import routers

from api.views_recipes import IngredientsViewSet, RecipeViewSet, TagsViewSet
from api.views_users import FollowApiView, ListFollowViewSet

router = routers.DefaultRouter()

router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagsViewSet, basename='tags')

urlpatterns = [
    path(
        'users/subscriptions/',
        ListFollowViewSet.as_view(),
        name='subscription',
    ),
    path(
        'users/<int:id>/subscribe/',
        FollowApiView.as_view(),
        name='subscribe',
    ),
    path('auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='logout'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
