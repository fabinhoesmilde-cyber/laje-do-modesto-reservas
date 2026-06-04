from rest_framework.routers import DefaultRouter
from .views import StatusReservaViewSet, ReservaViewSet

router = DefaultRouter()
router.register(r'status-reserva', StatusReservaViewSet)
router.register(r'reservas', ReservaViewSet)

urlpatterns = router.urls