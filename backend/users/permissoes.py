from rest_framework.permissions import BasePermission

from clientes.models import Cliente


class IsCliente(BasePermission):
    """
    Só deixa passar quem está logado como cliente: conta ativa, que não é
    da equipe (admin) e que está ligada a um cadastro de cliente.
    """

    def has_permission(self, request, view):
        usuario = request.user

        return bool(
            usuario
            and usuario.is_authenticated
            and usuario.is_active
            and not usuario.is_staff
            and Cliente.objects.filter(user=usuario).exists()
        )