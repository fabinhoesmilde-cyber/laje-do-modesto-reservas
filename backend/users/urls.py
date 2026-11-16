from django.urls import path

from .cadastro import cadastro_cliente, confirmar_cadastro

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
]