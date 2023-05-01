from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Чтение всем, публикации только авторизованным,
    правки - автор."""
    def has_object_permission(self, request, view, obj):
        user = request.user
        return any([
            request.method in permissions.SAFE_METHODS,
            request.method == 'POST' and user.is_authenticated,
            request.method in ('PATCH', 'DELETE') and obj.author == user,
        ])
