import json
import tempfile
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse

from restaurant.models import Order, RestaurantTable
from restaurant.reporting import create_excel_report


class PublicHttpContractTests(TestCase):
    def test_landing_page_returns_customer_homepage(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The Pattern Pizzeria')

    def test_order_api_creates_order_and_returns_documented_payload(self):
        table = RestaurantTable.objects.create(table_number=41)
        response = self.client.post(
            reverse('api_create_order'),
            data=json.dumps({
                'table_number': table.table_number,
                'customer_name': 'HTTP Guest',
                'category': 'veg',
                'item_name': 'HTTP Pizza',
                'price': 9.5,
            }),
            content_type='application/json',
        )
        payload = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(payload['success'])
        self.assertEqual(payload['orders'][0]['customer'], 'HTTP Guest')
        self.assertTrue(Order.objects.filter(customer_name='HTTP Guest').exists())

    def test_order_api_rejects_get_requests(self):
        response = self.client.get(reverse('api_create_order'))
        self.assertEqual(response.status_code, 405)

    def test_test_report_is_downloadable_as_an_excel_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            reports_directory = Path(temporary_directory) / 'test_reports'
            create_excel_report(
                reports_directory / 'unit.xlsx',
                {'title': 'Unit testing'},
                [{'test': 'example', 'status': 'PASS', 'duration_seconds': 0.01, 'details': ''}],
            )
            with override_settings(BASE_DIR=Path(temporary_directory)):
                response = self.client.get(reverse('download_test_report', args=['unit']))
                response.close()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        self.assertIn('unit_test_report.xlsx', response['Content-Disposition'])

    def test_missing_or_unknown_reports_are_not_served(self):
        self.assertEqual(
            self.client.get(reverse('download_test_report', args=['not-a-suite'])).status_code,
            404,
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            with override_settings(BASE_DIR=Path(temporary_directory)):
                response = self.client.get(reverse('download_test_report', args=['integration']))
        self.assertEqual(response.status_code, 404)
