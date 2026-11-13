from rest_framework.routers import DefaultRouter
from .views import AdicionalViewSet

router = DefaultRouter()
router.register(
    r'adicionais',
    AdicionalViewSet,
    basename='adicional'
)

urlpatterns = router.urls