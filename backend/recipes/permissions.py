from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Класс определения прав доступа."""

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, local_obj):
        # if (request.method in ['POST', 'PUT', 'PATCH', 'DELETE']
        if (request.method in ['PUT', 'PATCH', 'DELETE']
                and not request.user.is_anonymous):
            return (
                request.user == local_obj.author
                or request.user.is_superuser
                or request.user.is_admin()
            )
        return request.method in permissions.SAFE_METHODS
