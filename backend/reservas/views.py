from rest_framework import viewsets
from .models import StatusReserva, Reserva
from .serializers import StatusReservaSerializer, ReservaSerializer


class StatusReservaViewSet(viewsets.ModelViewSet):
    queryset = StatusReserva.objects.all()
    serializer_class = StatusReservaSerializer


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer