
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.decorators import throttle_classes
from rest_framework.throttling import AnonRateThrottle


class AdminLoginThrottle(AnonRateThrottle):
    scope = 'admin_login'
    rate = '10/hour'


@api_view(['POST'])
@throttle_classes([AdminLoginThrottle])
def admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(
        username=username,
        password=password
    )

    if not user:
        return Response(
            {'erro': 'Usuário ou senha inválidos'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Permite somente contas autorizadas como administradoras.
    if not (user.is_staff or user.is_superuser):
        return Response(
            {'erro': 'Acesso permitido apenas para administradores.'},
            status=status.HTTP_403_FORBIDDEN
        )

    token, created = Token.objects.get_or_create(user=user)

    return Response({
        'token': token.key,
        'username': user.username
    })
