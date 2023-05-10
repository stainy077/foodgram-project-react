from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import FollowSerializer, ShowFollowersSerializer
from foodgram.pagination import CustomPageNumberPaginator
from users.models import Follow

User = get_user_model()


class FollowApiView(APIView):
    """Подписаться/отписаться."""

    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        author = get_object_or_404(User, id=id)
        data = {'user': request.user.id, 'author': id}
        serializer = FollowSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        Follow.objects.create(user=request.user, author=author)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = get_object_or_404(Follow, user=user, author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListFollowViewSet(generics.ListAPIView):
    """Страница подписок."""

    permission_classes = [IsAuthenticated]
    serializer_class = ShowFollowersSerializer
    pagination_class = CustomPageNumberPaginator

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
