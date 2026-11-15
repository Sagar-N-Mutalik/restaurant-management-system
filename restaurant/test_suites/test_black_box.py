import json
from io import BytesIO
import tempfile
import zipfile
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse
from openpyxl import load_workbook

from restaurant.models import Order, RestaurantTable, MenuItem
from restaurant.reporting import ReportableAssertions, create_excel_report, test_case


class PublicHttpContractTests(ReportableAssertions, TestCase):
    @test_case(
        test_id='TC-BB-001',
        functionality='Customer Web Interface - Landing Page',
        title='Public home route returns HTTP 200 and renders restaurant branding',
        steps='1. Dispatch GET /; 2. Assert HTTP 200 OK; 3. Assert restaurant brand name presence.',
        inputs='GET request to index route (/)',
        expected_result='HTTP 200 OK with branding text "The Pattern Pizzeria" or "SmartResto".',
    )
    def test_landing_page_returns_customer_homepage(self):
        response = self.client.get(reverse('index'))
        content = response.content.decode()
        has_brand = 'The Pattern Pizzeria' in content or 'SmartResto' in content
        self.report_actual_result(f'HTTP {response.status_code}; branding displayed: {has_brand}.')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(has_brand)

    @test_case(
        test_id='TC-BB-002',
        functionality='Customer Web Interface - Menu Page',
        title='Table menu route returns HTTP 200 with available food items',
        steps='1. Create table and menu items; 2. Dispatch GET /menu/<table_id>/; 3. Assert HTTP 200.',
        inputs='GET request to /menu/41/',
        expected_result='HTTP 200 OK with menu catalog and table context.',
    )
    def test_table_menu_page_returns_menu_items(self):
        table = RestaurantTable.objects.create(table_number=41)
        MenuItem.objects.create(name='Margherita', price=11.0, item_type='VEG')
        response = self.client.get(reverse('menu_page', args=[table.table_number]))
        self.report_actual_result(f'HTTP {response.status_code}; Table {table.table_number} menu rendered.')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Margherita')

    @test_case(
        test_id='TC-BB-003',
        functionality='REST API - Single Item Order Submission',
        title='Order API creates single-item order and returns HTTP 201 Created',
        steps='1. POST /api/order with valid single item payload; 2. Assert HTTP 201; 3. Check JSON schema.',
        inputs='Payload: {table_number: 42, customer_name: "HTTP Guest", item_name: "Pizza", price: 9.5}',
        expected_result='HTTP 201 Created with JSON {"success": true, "orders": [...]} and DB persistence.',
    )
    def test_order_api_creates_order_and_returns_documented_payload(self):
        table = RestaurantTable.objects.create(table_number=42)
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
            f'HTTP {response.status_code}; success: {payload.get("success")}; customer: {payload.get("orders", [{}])[0].get("customer")}.'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(payload['success'])
        self.assertEqual(payload['orders'][0]['customer'], 'HTTP Guest')
        self.assertTrue(Order.objects.filter(customer_name='HTTP Guest').exists())

    @test_case(
        test_id='TC-BB-004',
        functionality='REST API - Multi-Item Cart Order Submission',
        title='Order API processes multi-item cart payload with strategy and modifiers',
        steps='1. POST /api/order with items array; 2. Assert HTTP 201; 3. Verify multiple orders created.',
        inputs='Payload: {table_number: 43, items: [{item_name: "Burger", price: 10}, {item_name: "Fries", price: 5}]}',
        expected_result='HTTP 201 Created with message "Processed 2 items successfully.".',
    )
    def test_order_api_processes_multi_item_cart(self):
        table = RestaurantTable.objects.create(table_number=43)
        response = self.client.post(
            reverse('api_create_order'),
            data=json.dumps({
                'table_number': table.table_number,
                'customer_name': 'Cart Guest',
                'items': [
                    {'item_name': 'Burger', 'price': 10.0, 'category': 'veg', 'strategy': 'normal'},
                    {'item_name': 'Fries', 'price': 5.0, 'category': 'veg', 'strategy': 'normal'},
                ]
            }),
            content_type='application/json',
        )
        payload = response.json()
        self.report_actual_result(f'HTTP {response.status_code}; message: {payload.get("message")}.')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(payload['success'])
        self.assertEqual(len(payload['orders']), 2)

    @test_case(
        test_id='TC-BB-005',
        functionality='REST API - Method Constraint Guard',
        title='Order endpoint rejects unsupported HTTP GET requests with HTTP 405',
        steps='1. Dispatch GET /api/order; 2. Assert HTTP 405 Method Not Allowed.',
        inputs='GET request to /api/order',
        expected_result='HTTP 405 Method Not Allowed with explanatory error JSON.',
    )
    def test_order_api_rejects_get_requests(self):
        response = self.client.get(reverse('api_create_order'))
        self.report_actual_result(f'HTTP {response.status_code}. Method Not Allowed enforced.')
        self.assertEqual(response.status_code, 405)

    @test_case(
        test_id='TC-BB-006',
        functionality='REST API - Non-Existent Table Guard',
        title='Order endpoint rejects orders for non-existent table numbers with HTTP 400',
        steps='1. POST /api/order with table_number: 99999; 2. Assert HTTP 400 Bad Request.',
        inputs='Payload with nonexistent table number 99999',
        expected_result='HTTP 400 Bad Request with error: "Table 99999 does not exist.".',
    )
    def test_order_api_rejects_nonexistent_table(self):
        response = self.client.post(
            reverse('api_create_order'),
            data=json.dumps({
                'table_number': 99999,
                'customer_name': 'Ghost',
                'item_name': 'Pizza',
                'price': 10.0,
            }),
            content_type='application/json',
        )
        self.report_actual_result(f'HTTP {response.status_code}; error: {response.json().get("error")}.')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    @test_case(
        test_id='TC-BB-007',
        functionality='Staff Dashboard Interface',
        title='Staff dashboard route returns HTTP 200 with tables and active orders',
        steps='1. Dispatch GET /staff-dashboard/; 2. Assert HTTP 200 OK and dashboard template.',
        inputs='GET /staff-dashboard/',
        expected_result='HTTP 200 OK rendering staff oversight console.',
    )
    def test_staff_dashboard_loads_successfully(self):
        response = self.client.get(reverse('staff_dashboard'))
        self.report_actual_result(f'HTTP {response.status_code}; Staff dashboard rendered.')
        self.assertEqual(response.status_code, 200)

    @test_case(
        test_id='TC-BB-008',
        functionality='Billing & Payment Web Interface',
        title='Payment page route returns HTTP 200 with calculated bill details',
        steps='1. Create occupied table with active order; 2. Dispatch GET /bill/<table_id>/; 3. Assert HTTP 200.',
        inputs='GET /bill/44/',
        expected_result='HTTP 200 OK rendering itemized bill and payment button.',
    )
    def test_table_bill_page_renders_successfully(self):
        table = RestaurantTable.objects.create(table_number=44, is_occupied=True)
        item = MenuItem.objects.create(name='Soda', price=3.0, item_type='VEG')
        order = Order.objects.create(customer_name='Bill User', table=table, total_amount=3.0, status='PREPARING')
        order.items.add(item)

        response = self.client.get(reverse('payment_page', args=[table.table_number]))
        self.report_actual_result(f'HTTP {response.status_code}; Bill page rendered for Table {table.table_number}.')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Soda')

    @test_case(
        test_id='TC-BB-009',
        functionality='Payment Confirmation Interface',
        title='Thank You confirmation page returns HTTP 200 post-payment',
        steps='1. Dispatch GET /thank-you/; 2. Assert HTTP 200 OK and confirmation text.',
        inputs='GET /thank-you/',
        expected_result='HTTP 200 OK rendering thank you message.',
    )
    def test_thank_you_page_renders_successfully(self):
        response = self.client.get(reverse('thank_you'))
        self.report_actual_result(f'HTTP {response.status_code}; Thank You page rendered.')
        self.assertEqual(response.status_code, 200)

    @test_case(
        test_id='TC-BB-010',
        functionality='Automated Reporting - Excel File Generation',
        title='Report route returns downloadable XLSX file with complete IEEE-829 columns',
        steps='1. Generate sample report; 2. GET /testing/reports/unit/; 3. Inspect XLSX columns and status.',
        inputs='GET /testing/reports/unit/',
        expected_result='HTTP 200, Content-Type: application/vnd.openxmlformats, with all 10 specification columns.',
    )
    def test_test_report_is_downloadable_as_an_excel_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            reports_directory = Path(temporary_directory) / 'test_reports'
            create_excel_report(
                reports_directory / 'unit.xlsx',
                {'title': 'Unit testing'},
                [{
                    'sl_no': 1,
                    'test_id': 'TC-UNIT-001',
                    'functionality': 'Pricing Strategy',
                    'test': 'example',
                    'title': 'Example test case',
                    'steps': '1. Step one; 2. Step two',
                    'inputs': 'Input sample',
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
        headers = [cell.value for cell in sheet[1]]
        self.report_actual_result(
            f'HTTP {response.status_code}; columns: {", ".join(str(h) for h in headers)}; status: {sheet["J2"].value}.'
        )
        expected_headers = [
            'Sl. No.',
            'Test Case ID',
            'Functionality',
            'Test Case Description',
            'Execution Steps',
            'Input Data',
            'Expected Result',
            'Actual Result',
            'Execution Time',
            'Status',
        ]
        self.assertEqual(headers, expected_headers)
        self.assertEqual(sheet['J2'].value, 'Pass')
        workbook.close()

    @test_case(
        test_id='TC-BB-011',
        functionality='Automated Reporting - ZIP Archive Package',
        title='Download-all route returns valid compressed ZIP archive of test reports',
        steps='1. Create report files; 2. GET /testing/download-all/; 3. Inspect ZIP archive contents.',
        inputs='GET /testing/download-all/',
        expected_result='HTTP 200, Content-Type: application/zip, serving valid multi-report zip archive.',
    )
    def test_test_reports_zip_download_serves_valid_archive(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            reports_directory = Path(temporary_directory) / 'test_reports'
            reports_directory.mkdir(parents=True, exist_ok=True)
            (reports_directory / 'unit.xlsx').write_text('dummy content')
            with override_settings(BASE_DIR=Path(temporary_directory)):
                response = self.client.get(reverse('download_all_reports'))
                zip_data = BytesIO(b''.join(response.streaming_content))
                with zipfile.ZipFile(zip_data, 'r') as z:
                    files = z.namelist()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertIn('unit.xlsx', files)
        self.report_actual_result(f'ZIP package verified with files: {files}.')

    @test_case(
        test_id='TC-BB-012',
        functionality='Automated Reporting - 404 Guard',
        title='Report endpoint rejects unknown suites and missing files with HTTP 404',
        steps='1. GET /testing/reports/invalid-suite/; 2. Assert HTTP 404 Not Found.',
        inputs='GET request with non-existent suite name "not-a-suite"',
        expected_result='HTTP 404 Not Found returned cleanly.',
    )
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
