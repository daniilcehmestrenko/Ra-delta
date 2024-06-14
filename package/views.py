from rest_framework import status
from rest_framework import mixins, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from package.models import Package, TypePackage, DeliveryCompany
from package.tasks import calculate_delivery_cost_for_all_packages_task, update_usd_rate_in_rub_task
from package.serializers import (
    ListPackageSerializer, TypePackageSerializer,
    DeliveryCompanySerializer, CreatePackageSerializer,
    RetrievePackageSerializer, AddCompanySerializer,
)


@api_view(['GET'])
def update_usd_rate_in_rub(request):
    """Run update usd rate task"""
    update_usd_rate_in_rub_task.delay()
    return Response({'message': 'Задача обновления курса доллара запущена.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def calculate_delivery_cost_for_all_packages(request):
    """Run calculate delivery cost task"""
    calculate_delivery_cost_for_all_packages_task.delay()
    return Response({'message': 'Задача пересчета стоимости доставки запущена.'}, status=status.HTTP_200_OK)


class PackageViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    queryset = Package.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type_package', 'delivery_cost']

    def __get_session_id(self):
        if self.request.session.session_key is None:
            self.request.session.save()
        return self.request.session.session_key

    def get_queryset(self):
        session_id = self.__get_session_id()
        return Package.objects.filter(session_id=session_id)

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
        """Binds the parcel to a company if no company is selected"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = get_object_or_404(DeliveryCompany, pk=serializer.data['company_id'])
        with transaction.atomic():
            package_list = Package.objects.select_for_update().filter(pk=kwargs['pk'], delivery_company__isnull=True)
            if len(package_list):
                package_list.update(delivery_company=company)
                return Response({'message': f'Компания {company.name} выбрана перевозчиком.'},
                                status=status.HTTP_200_OK)
        return Response(
            {'message': f'Компания {company.name} не может быть выбрана перевозчиком либо уже выбрана.'},
            status=status.HTTP_200_OK
        )

    def retrieve(self, request, *args, **kwargs):
        """Detail view for Package instance"""
        session_id = self.__get_session_id()
        instance = self.get_object()
        if session_id == str(instance.session_id):
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({'message': 'Не найдено'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        """Create Package instance"""
        session_id = self.__get_session_id()

        new_data = request.data.copy()
        new_data.update(session=session_id)

        serializer = self.get_serializer(data=new_data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TypePackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TypePackage.objects.all()
    serializer_class = TypePackageSerializer


class DeliveryCompanyViewSet(viewsets.ModelViewSet):
    queryset = DeliveryCompany.objects.all()
    serializer_class = DeliveryCompanySerializer
