from django.urls import include, path
from rest_framework import routers

from package.views import PackageViewSet, TypePackageViewSet, DeliveryCompanyViewSet, calculate_delivery_cost_view


router = routers.DefaultRouter()
router.register(r'package', PackageViewSet)
router.register(r'type_package', TypePackageViewSet)
router.register(r'delivery_company', DeliveryCompanyViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('calculate/', calculate_delivery_cost_view),
]
