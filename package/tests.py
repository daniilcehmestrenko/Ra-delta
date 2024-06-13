from django.urls import reverse
from django.contrib.sessions.models import Session

from rest_framework import status
from rest_framework.test import APITestCase

from package.service import delivery_cost_calculation
from package.models import Package, TypePackage, DeliveryCompany


class PackageTests(APITestCase):
    def setUp(self):
        self.package_data = {
          "name": "test_name",
          "weight": "5.000",
          "cost_in_usd": "12.00",
          "delivery_cost": None,
          "session": None,
          "type_package": 1,
          "delivery_company": None,
        }

    def create_package(self):
        self.client.session.save()
        type_package = TypePackage.objects.create(name=TypePackage.CLOTH)
        session = Session.objects.get(session_key=self.client.session.session_key)
        self.package_data['type_package'] = type_package
        self.package_data['session'] = session
        return Package.objects.create(**self.package_data)

    def test_delivery_cost_calculation(self):
        cost = delivery_cost_calculation(2, 12.3, 89)

        self.assertEqual(cost, 99.947)

    def test_create_package(self):
        type_package = TypePackage.objects.create(name=TypePackage.ELECTRONIC)
        self.package_data['type_package'] = type_package.pk
        url = reverse('package-list')
        response = self.client.post(url, self.package_data, format='json')
        data = response.json()

        package = Package.objects.filter(pk=data['id']).first()

        self.assertTrue(package)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.package_data['name'], package.name)

    def test_get_package(self):
        package = self.create_package()
        url = reverse('package-list')
        response = self.client.get(url)
        data = response.json()
        count_packages = Package.objects.all().count()

        self.assertEqual(type(data['results']), list)
        self.assertEqual(len(data['results']), count_packages)
        self.assertEqual(str(package.pk), data['results'][-1]['id'])
        self.assertEqual(package.name, data['results'][-1]['name'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail_package(self):
        package = self.create_package()
        url = reverse('package-detail', kwargs={'pk': str(package.id)})
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(data['name'], package.name)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_company(self):
        package = self.create_package()
        company = DeliveryCompany.objects.create(name='test_company')
        url = reverse('package-add-company', kwargs={'pk': str(package.id)})
        response = self.client.post(url, {'company_id': company.pk}, format='json')
        data = response.json()
        updated_package = Package.objects.get(id=package.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_package.delivery_company.pk, company.pk)
        self.assertEqual(data['message'], f'Компания {company.name} выбрана перевозчиком.')


class TypePackageTest(APITestCase):
    fixtures = ['subjects.json']

    def test_get_type_package(self):
        url = reverse('typepackage-list')
        response = self.client.get(url)
        data = response.json()
        count_types = TypePackage.objects.all().count()

        self.assertEqual(len(data['results']), count_types)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_type_package_detail(self):
        url = reverse('typepackage-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(data['name'], 'CL')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DeliveryCompanyTest(APITestCase):
    def setUp(self):
        self.name = 'test_company'

    def create_company(self):
        return DeliveryCompany.objects.create(name=self.name)

    def test_get_delivery_company(self):
        self.create_company()
        url = reverse('deliverycompany-list')
        response = self.client.get(url)
        data = response.json()
        count_company = DeliveryCompany.objects.all().count()

        self.assertEqual(len(data['results']), count_company)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_delivery_company_detail(self):
        company = self.create_company()
        url = reverse('deliverycompany-detail', kwargs={'pk': company.pk})
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(data['id'], company.pk)
        self.assertEqual(data['name'], company.name)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_delivery_company(self):
        url = reverse('deliverycompany-list')
        response = self.client.post(url, {'name': 'test_company'}, format='json')
        data = response.json()
        count_company = DeliveryCompany.objects.all().count()

        self.assertEqual(count_company, 1)
        self.assertEqual(data['name'], 'test_company')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
