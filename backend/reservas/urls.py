from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    StatusReservaViewSet,
    ReservaViewSet,
    consultar_reserva,
    solicitar_cancelamento,
    solicitar_alteracao,
    aprovar_alteracao,
    rejeitar_alteracao,
    aprovar_cancelamento,
    rejeitar_cancelamento,
    criar_reserva
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

    path(
        'aprovar-alteracao/',
        aprovar_alteracao,
        name='aprovar-alteracao'
    ),

    path(
        'rejeitar-alteracao/',
        rejeitar_alteracao,
        name='rejeitar-alteracao'
    ),
    path(
        'aprovar-cancelamento/',
        aprovar_cancelamento,
        name='aprovar-cancelamento'
    ),
    path(
        'rejeitar-cancelamento/',
        rejeitar_cancelamento,
        name='rejeitar-cancelamento'
    ),
    path(
        'criar-reserva/',
        criar_reserva,
        name='criar-reserva'
),
]