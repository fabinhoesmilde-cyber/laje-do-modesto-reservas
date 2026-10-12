
from rest_framework import serializers
from .models import Cupom


class CupomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cupom
        fields = "__all__"

    def validate_codigo(self, value):
        codigo = value.strip().upper()

        if not codigo:
            raise serializers.ValidationError(
                "O código do cupom não pode ficar vazio."
            )

        return codigo

    def validate_tipo_desconto(self, value):
        tipo = value.strip().lower()

        tipos_validos = ["percentual", "fixo"]

        if tipo not in tipos_validos:
            raise serializers.ValidationError(
                "O tipo de desconto deve ser 'percentual' ou 'fixo'."
            )

        return tipo

    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "O valor do desconto deve ser maior que zero."
            )

        if self.initial_data.get("tipo_desconto", "").strip().lower() == "percentual":
            if value > 100:
                raise serializers.ValidationError(
                    "O desconto percentual não pode ultrapassar 100%."
                )

        return value
