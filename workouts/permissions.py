from rest_framework import permissions

class IsTrainer(permissions.BasePermission):
    """
    Allows access only to trainer users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_trainer