from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication

from config.permissions import IsAdminOrReadOnly

from .models import DiaBloqueado
from .serializers import DiaBloqueadoSerializer


class DiaBloqueadoViewSet(viewsets.ModelViewSet):

    queryset = DiaBloqueado.objects.all().order_by("data")
    serializer_class = DiaBloqueadoSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]