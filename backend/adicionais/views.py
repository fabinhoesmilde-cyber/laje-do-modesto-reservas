from rest_framework import viewsets
from .models import Adicional
from .serializers import AdicionalSerializer


class AdicionalViewSet(viewsets.ModelViewSet):
    queryset = Adicional.objects.all()
    serializer_class = AdicionalSerializer