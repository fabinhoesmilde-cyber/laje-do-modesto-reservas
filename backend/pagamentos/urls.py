from rest_framework.routers import DefaultRouter
from .views import PagamentoViewSet

router = DefaultRouter()
router.register(r'pagamentos', PagamentoViewSet)

urlpatterns = router.urls