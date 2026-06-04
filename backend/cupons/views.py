from rest_framework import viewsets
from .models import Cupom
from .serializers import CupomSerializer


class CupomViewSet(viewsets.ModelViewSet):
    queryset = Cupom.objects.all()
    serializer_class = CupomSerializer