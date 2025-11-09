from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, LocationViewSet

router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'locations', LocationViewSet, basename='location')

urlpatterns = router.urls
