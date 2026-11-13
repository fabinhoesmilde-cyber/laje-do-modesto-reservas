from rest_framework.generics import RetrieveAPIView
from .models import Configuracao
from .serializers import ConfiguracaoSerializer


class ConfiguracaoAPIView(RetrieveAPIView):

    serializer_class = ConfiguracaoSerializer

    def get_object(self):
        configuracao, created = Configuracao.objects.get_or_create(pk=1)
        return configuracao