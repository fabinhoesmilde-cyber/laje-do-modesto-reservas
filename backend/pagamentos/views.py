
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication

from config.permissions import IsAdminUser
from .models import Pagamento
from .serializers import PagamentoSerializer


class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
