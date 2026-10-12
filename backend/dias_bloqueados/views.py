
from rest_framework import viewsets
from .models import DiaBloqueado
from .serializers import DiaBloqueadoSerializer


class DiaBloqueadoViewSet(viewsets.ModelViewSet):
    queryset = DiaBloqueado.objects.all().order_by("data")
    serializer_class = DiaBloqueadoSerializer
