from rest_framework import status
from rest_framework import mixins, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from package.utils import get_usd_rate_from_cache
from package.service import delivery_cost_calculation
from package.models import Package, TypePackage, DeliveryCompany
from package.serializers import (
    ListPackageSerializer, TypePackageSerializer,
    DeliveryCompanySerializer, CreatePackageSerializer,
    RetrievePackageSerializer, AddCompanySerializer,
)


@api_view(['POST'])
def calculate_delivery_cost_view(request):
    usd_rate_in_rub = get_usd_rate_from_cache()
    if usd_rate_in_rub is None:
        return Response({'message': 'Расчет стоимости доставки недоступен, попробуйте позже.'})
    package = get_object_or_404(Package, pk=request.data.get('package_id'))
    package.delivery_cost = delivery_cost_calculation(package.weight, package.cost_in_usd, usd_rate_in_rub)
    package.save()
    return Response({'message': 'Расчет стоимости прошел успешно.'})


class PackageViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    queryset = Package.objects.all()

    def __get_session_id(self):
        if self.request.session.session_key is None:
            self.request.session.save()
        return self.request.session.session_key

    def get_queryset(self):
        session_id = self.__get_session_id()
        return Package.objects.filter(session=session_id)

    def perform_create(self, serializer):
        return serializer.save()

    def get_serializer_class(self):
        serializer_map = {
            'list': ListPackageSerializer,
            'create': CreatePackageSerializer,
            'retrieve': RetrievePackageSerializer,
            'add_company': AddCompanySerializer,
        }
        serializer = serializer_map.get(self.action)
        assert serializer is not None
        return serializer

    @action(methods=['post'], detail=True, url_path='add_company', url_name='add-company')
    def add_company(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = get_object_or_404(DeliveryCompany, pk=serializer.data['company_id'])
        package = get_object_or_404(Package, pk=kwargs['pk'])
        package.delivery_company = company
        package.save()
        return Response({'message': f'Компания {company.name} выбрана перевозчиком.'})

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if request.query_params:
            if type_package := request.query_params.get('type_package'):
                queryset = queryset.filter(type_package__name=type_package)
            elif request.query_params.get('delivery_cost'):
                queryset = queryset.filter(delivery_cost__isnull=False)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        session_id = self.__get_session_id()
        instance = self.get_object()
        if session_id == str(instance.session_id):
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({'message': 'У вас нет доступа к этой посылке.'})

    def create(self, request, *args, **kwargs):
        session_id = self.__get_session_id()
        usd_rate_in_rub = get_usd_rate_from_cache()

        new_data = request.data.copy()
        new_data.update(session=session_id)

        serializer = self.get_serializer(data=new_data)
        serializer.is_valid(raise_exception=True)

        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if usd_rate_in_rub:
            delivery_cost = delivery_cost_calculation(instance.weight, instance.cost_in_usd, usd_rate_in_rub)
            instance.delivery_cost = delivery_cost
            instance.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TypePackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TypePackage.objects.all()
    serializer_class = TypePackageSerializer


class DeliveryCompanyViewSet(viewsets.ModelViewSet):
    queryset = DeliveryCompany.objects.all()
    serializer_class = DeliveryCompanySerializer
