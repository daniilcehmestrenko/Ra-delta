from django.urls import include, path
from rest_framework import routers

from package.views import (
    PackageViewSet, TypePackageViewSet, DeliveryCompanyViewSet,
    calculate_delivery_cost_for_all_packages, update_usd_rate_in_rub
)


router = routers.DefaultRouter()
router.register(r'package', PackageViewSet)
router.register(r'type_package', TypePackageViewSet)
router.register(r'delivery_company', DeliveryCompanyViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('update_usd_rate/', update_usd_rate_in_rub),
    path('calculate_delivery_cost/', calculate_delivery_cost_for_all_packages),
]
