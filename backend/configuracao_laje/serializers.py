from rest_framework import serializers
from .models import ConfiguracaoReserva


class ConfiguracaoReservaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConfiguracaoReserva
        fields = "__all__"