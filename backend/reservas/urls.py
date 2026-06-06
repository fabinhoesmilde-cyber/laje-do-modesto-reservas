from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    StatusReservaViewSet,
    ReservaViewSet,
    consultar_reserva,
    solicitar_cancelamento,
    solicitar_alteracao
)

router = DefaultRouter()
router.register(r'status-reserva', StatusReservaViewSet)
router.register(r'reservas', ReservaViewSet)

urlpatterns = router.urls + [
    path(
        'consultar-reserva/',
        consultar_reserva,
        name='consultar-reserva'
    ),

    path(
        'solicitar-cancelamento/',
        solicitar_cancelamento,
        name='solicitar-cancelamento'
    ),

    path(
        'solicitar-alteracao/',
        solicitar_alteracao,
        name='solicitar-alteracao'
    ),
]