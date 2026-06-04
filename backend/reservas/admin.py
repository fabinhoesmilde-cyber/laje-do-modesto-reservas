from django.contrib import admin
from .models import StatusReserva, Reserva, ReservaAdicional

admin.site.register(StatusReserva)
admin.site.register(Reserva)
admin.site.register(ReservaAdicional)