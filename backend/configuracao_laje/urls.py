from django.urls import path
from .views import ConfiguracaoReservaView


urlpatterns = [
    path(
        "reserva/",
        ConfiguracaoReservaView.as_view(),
        name="configuracao-reserva"
    ),
]