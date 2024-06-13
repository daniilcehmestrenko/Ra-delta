from django.contrib import admin

from package.models import TypePackage, Package, DeliveryCompany


admin.site.register(TypePackage)
admin.site.register(Package)
admin.site.register(DeliveryCompany)
