
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import SAFE_METHODS, BasePermission

from config.permissions import IsAdminUser
from .models import Adicional
from .serializers import AdicionalSerializer


class AdicionalPermission(BasePermission):

    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return True

        return IsAdminUser().has_permission(request, view)


class AdicionalViewSet(viewsets.ModelViewSet):
    serializer_class = AdicionalSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [AdicionalPermission]

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return Adicional.objects.all()

        return Adicional.objects.filter(ativo=True)
