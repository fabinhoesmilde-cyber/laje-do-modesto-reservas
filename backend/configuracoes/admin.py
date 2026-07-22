from django.contrib import admin
from .models import Configuracao


@admin.register(Configuracao)
class ConfiguracaoAdmin(admin.ModelAdmin):

    list_display = (
        "valor_reserva",
        "valor_hora_extra",
        "duracao_reserva",
        "horario_limite",
    )

    def has_add_permission(self, request):
        return not Configuracao.objects.exists()