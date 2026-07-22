from django.urls import path
from .views import ConfiguracaoAPIView

urlpatterns = [
    path("", ConfiguracaoAPIView.as_view(), name="configuracoes"),
]