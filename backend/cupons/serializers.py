from rest_framework import serializers
from .models import Cupom


class CupomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cupom
        fields = "__all__"

        read_only_fields = [
            "uso_atual",
            "criado_em",
        ]

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

        tipo = self.initial_data.get(
            "tipo_desconto",
            getattr(self.instance, "tipo_desconto", "")
        ).strip().lower()

        if tipo == "percentual" and value > 100:
            raise serializers.ValidationError(
                "O desconto percentual não pode ultrapassar 100%."
            )

        return value

    def validate_desconto_maximo(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "O desconto máximo deve ser maior que zero."
            )

        return value


    def validate(self, attrs):
        data_inicio = attrs.get(
            "data_inicio",
            getattr(self.instance, "data_inicio", None)
        )
        data_fim = attrs.get(
            "data_fim",
            getattr(self.instance, "data_fim", None)
        )
        validade = attrs.get(
            "validade",
            getattr(self.instance, "validade", None)
        )

        if not data_inicio:
            raise serializers.ValidationError({
                "data_inicio": "A data inicial é obrigatória."
            })

        if not data_fim:
            raise serializers.ValidationError({
                "data_fim": "A data final é obrigatória."
            })

        if data_inicio > data_fim:
            raise serializers.ValidationError({
                "data_fim": "A data final não pode ser anterior à data inicial."
            })

        if not validade:
            raise serializers.ValidationError({
                "validade": "A validade do cupom é obrigatória."
            })

        if validade < data_inicio:
            raise serializers.ValidationError({
                "validade": "A validade não pode ser anterior à data inicial."
            })

        if data_fim > validade:
            raise serializers.ValidationError({
                "data_fim": "A data final de utilização não pode ultrapassar a validade do cupom."
            })

        return attrs
