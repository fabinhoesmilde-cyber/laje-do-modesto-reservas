
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication

from config.permissions import IsAdminUser
from .models import Cupom
from .serializers import CupomSerializer


class CupomViewSet(viewsets.ModelViewSet):
    queryset = Cupom.objects.all()
    serializer_class = CupomSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
