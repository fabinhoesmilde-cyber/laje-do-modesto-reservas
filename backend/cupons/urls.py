from rest_framework.routers import DefaultRouter
from .views import CupomViewSet

router = DefaultRouter()
router.register(r'cupons', CupomViewSet)

urlpatterns = router.urls