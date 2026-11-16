from django.urls import path

from .cadastro import cadastro_cliente, confirmar_cadastro
from .acoes_cliente import alterar_minha_reserva, cancelar_minha_reserva
from .login import login_cliente, logout_cliente, meus_dados
from .minhas_reservas import detalhe_reserva, minhas_reservas

urlpatterns = [
    path(
        'cliente/cadastro/',
        cadastro_cliente,
        name='cliente-cadastro'
    ),
    path(
        'cliente/confirmar-cadastro/',
        confirmar_cadastro,
        name='cliente-confirmar-cadastro'
    ),
    path(
        'cliente/login/',
        login_cliente,
        name='cliente-login'
    ),
    path(
        'cliente/logout/',
        logout_cliente,
        name='cliente-logout'
    ),
    path(
        'cliente/meus-dados/',
        meus_dados,
        name='cliente-meus-dados'
    ),
    path(
        'cliente/minhas-reservas/',
        minhas_reservas,
        name='cliente-minhas-reservas'
    ),
    path(
        'cliente/minhas-reservas/<str:codigo>/',
        detalhe_reserva,
        name='cliente-detalhe-reserva'
    ),
    path(
        'cliente/minhas-reservas/<str:codigo>/cancelar/',
        cancelar_minha_reserva,
        name='cliente-cancelar-reserva'
    ),
    path(
        'cliente/minhas-reservas/<str:codigo>/alterar/',
        alterar_minha_reserva,
        name='cliente-alterar-reserva'
    ),
]