import json
from io import BytesIO
import tempfile
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse
from openpyxl import load_workbook

from restaurant.models import Order, RestaurantTable
from restaurant.reporting import ReportableAssertions, create_excel_report, test_case


class PublicHttpContractTests(ReportableAssertions, TestCase):
    @test_case('Black-box - Open home page', 'The public home route returns HTTP 200 and displays the landing-page heading.')
    def test_landing_page_returns_customer_homepage(self):
        response = self.client.get(reverse('index'))
        self.report_actual_result(f'HTTP {response.status_code}; landing heading displayed: {"The Pattern Pizzeria" in response.content.decode()}.')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The Pattern Pizzeria')

    @test_case(
        'Black-box - Submit valid order',
        'The order API returns HTTP 201, confirms success, returns the customer name, and persists the order.',
    )
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
        self.report_actual_result(
            f'HTTP {response.status_code}; success: {payload.get("success")}; '
            f'customer: {payload.get("orders", [{}])[0].get("customer")}; '
            f'order persisted: {Order.objects.filter(customer_name="HTTP Guest").exists()}.'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(payload['success'])
        self.assertEqual(payload['orders'][0]['customer'], 'HTTP Guest')
        self.assertTrue(Order.objects.filter(customer_name='HTTP Guest').exists())

    @test_case('Black-box - Reject GET order request', 'The order endpoint rejects GET requests with HTTP 405.')
    def test_order_api_rejects_get_requests(self):
        response = self.client.get(reverse('api_create_order'))
        self.report_actual_result(f'HTTP {response.status_code}.')
        self.assertEqual(response.status_code, 405)

    @test_case(
        'Black-box - Download Excel report',
        'The report route returns a downloadable XLSX file with Test Case, Expected Result, Actual Result, and Remark columns.',
    )
    def test_test_report_is_downloadable_as_an_excel_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            reports_directory = Path(temporary_directory) / 'test_reports'
            create_excel_report(
                reports_directory / 'unit.xlsx',
                {'title': 'Unit testing'},
                [{
                    'test': 'example',
                    'title': 'Example test case',
                    'expected_result': 'Example behavior is expected.',
                    'actual_result': 'Example behavior observed.',
                    'status': 'PASS',
                    'remark': 'Pass',
                    'duration_seconds': 0.01,
                    'details': '',
                }],
            )
            with override_settings(BASE_DIR=Path(temporary_directory)):
                response = self.client.get(reverse('download_test_report', args=['unit']))
                workbook = load_workbook(BytesIO(b''.join(response.streaming_content)), read_only=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        self.assertIn('unit_test_report.xlsx', response['Content-Disposition'])
        sheet = workbook['Test Cases']
        self.report_actual_result(
            f'HTTP {response.status_code}; columns: {", ".join(str(cell.value) for cell in sheet[1])}; '
            f'example remark: {sheet["D2"].value}.'
        )
        self.assertEqual(
            [cell.value for cell in sheet[1]],
            ['Test Case', 'Expected Result', 'Actual Result', 'Remark'],
        )
        self.assertEqual(sheet['D2'].value, 'Pass')
        self.assertEqual([sheet.cell(row=row, column=1).value for row in range(4, 8)],
                         ['Total', 'Pass', 'Fail', 'Not Executed'])
        self.assertEqual([sheet.cell(row=row, column=2).value for row in range(4, 8)], [1, 1, 0, 0])
        workbook.close()

    @test_case('Black-box - Reject unavailable report', 'Unknown suites and reports that are not present return HTTP 404.')
    def test_missing_or_unknown_reports_are_not_served(self):
        unknown_response = self.client.get(reverse('download_test_report', args=['not-a-suite']))
        with tempfile.TemporaryDirectory() as temporary_directory:
            with override_settings(BASE_DIR=Path(temporary_directory)):
                response = self.client.get(reverse('download_test_report', args=['integration']))
        self.report_actual_result(
            f'Unknown suite: HTTP {unknown_response.status_code}; missing report: HTTP {response.status_code}.'
        )
        self.assertEqual(unknown_response.status_code, 404)
        self.assertEqual(response.status_code, 404)
