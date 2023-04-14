from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from foodgram.pagination import CustomPageNumberPaginator
from users.models import Follow
from users.serializers import FollowSerializer, ShowFollowersSerializer

User = get_user_model()


class FollowApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        data = {'user': request.user.id, 'author': id}
        serializer = FollowSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        try:
            subscription = Follow.objects.get(user=user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response(
                'Ошибка отписки',
                status=status.HTTP_400_BAD_REQUEST,
            )


class ListFollowViewSet(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShowFollowersSerializer
    pagination_class = CustomPageNumberPaginator

    def get_queryset(self):
        user = self.request.user
        if User.objects.filter(following__user=user).exists():
            return User.objects.filter(following__user=user)
        return Response(
            'У Вас нет подписок!',
            status=status.HTTP_400_BAD_REQUEST,
        )
