from django.urls import path, include
from djoser.views import TokenCreateView, TokenDestroyView

from users.views import FollowApiView, ListFollowViewSet

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
    path('', include('djoser.urls')),
]
