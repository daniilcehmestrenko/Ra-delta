from rest_framework import serializers

from package.models import Package, TypePackage, DeliveryCompany


class AddCompanySerializer(serializers.Serializer):
    company_id = serializers.IntegerField()


class ListPackageSerializer(serializers.ModelSerializer):
    type_package_name = serializers.CharField()
    delivery_cost = serializers.SerializerMethodField('delivery_cost_info')

    def delivery_cost_info(self, obj):
        return obj.delivery_cost if obj.delivery_cost else 'Не рассчитано'

    class Meta:
        model = Package
        fields = ('id', 'name', 'type_package_name', 'weight', 'cost_in_usd', 'delivery_cost', 'delivery_company')


class CreatePackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'


class RetrievePackageSerializer(serializers.ModelSerializer):
    type_package_name = serializers.CharField()
    delivery_cost = serializers.SerializerMethodField('delivery_cost_info')

    def delivery_cost_info(self, obj):
        return obj.delivery_cost if obj.delivery_cost else 'Не рассчитано'

    class Meta:
        model = Package
        fields = ('name', 'type_package_name', 'weight', 'cost_in_usd', 'delivery_cost')


class TypePackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypePackage
        fields = '__all__'


class DeliveryCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCompany
        fields = '__all__'
