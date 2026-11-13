from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication

from config.permissions import IsAdminOrReadOnly

from .models import ConfiguracaoReserva
from .serializers import ConfiguracaoReservaSerializer


class ConfiguracaoReservaView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):

        configuracao, created = (
            ConfiguracaoReserva.objects.get_or_create(
                pk=1
            )
        )

        serializer = ConfiguracaoReservaSerializer(
            configuracao
        )

        return Response(serializer.data)

    def put(self, request):

        configuracao, created = (
            ConfiguracaoReserva.objects.get_or_create(
                pk=1
            )
        )

        serializer = ConfiguracaoReservaSerializer(
            configuracao,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )