from django.urls import path
from rest_framework.routers import DefaultRouter
from .disponibilidade_publica import disponibilidade

from .views import (
    StatusReservaViewSet,
    ReservaViewSet,
    consultar_reserva,
    aprovar_alteracao,
    rejeitar_alteracao,
    aprovar_cancelamento,
    rejeitar_cancelamento,
    criar_reserva,
    validar_cupom
)


router = DefaultRouter()
router.register(r'status-reserva', StatusReservaViewSet)
router.register(r'reservas', ReservaViewSet)

urlpatterns = router.urls + [
        path(
        'disponibilidade/',
        disponibilidade,
        name='disponibilidade'
    ),
    
    path(
        'consultar-reserva/',
        consultar_reserva,
        name='consultar-reserva'
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
        path(
        'validar-cupom/',
        validar_cupom,
        name='validar-cupom'
    ),
]