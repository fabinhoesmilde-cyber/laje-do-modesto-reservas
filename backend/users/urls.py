from django.urls import path

from .cadastro import cadastro_cliente, confirmar_cadastro
from .login import login_cliente, logout_cliente, meus_dados

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
]