
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUser(BasePermission):

    message = "Acesso permitido somente para administradores."

    def has_permission(self, request, view):
        user = request.user

        return (
            user
            and user.is_authenticated
            and (user.is_staff or user.is_superuser)
        )


class IsAdminOrReadOnly(BasePermission):

    message = "Somente administradores podem realizar alterações."

    def has_permission(self, request, view):

        # Permite consultas públicas.
        if request.method in SAFE_METHODS:
            return True

        # Exige administrador para alterações.
        user = request.user

        return (
            user
            and user.is_authenticated
            and (user.is_staff or user.is_superuser)
        )
