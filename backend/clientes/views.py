
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication

from config.permissions import IsAdminUser
from .models import Cliente
from .serializers import ClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
