from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status


@api_view(['POST'])
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

    token, created = Token.objects.get_or_create(
        user=user
    )

    return Response({
        'token': token.key,
        'username': user.username
    })