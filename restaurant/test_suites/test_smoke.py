from django.test import TestCase
from django.urls import reverse

from restaurant.models import RestaurantTable
from restaurant.reporting import ReportableAssertions, test_case


class MainPageSmokeTests(ReportableAssertions, TestCase):
    def setUp(self):
        self.table = RestaurantTable.objects.create(table_number=61)

    @test_case(
        test_id='TC-SMK-001',
        functionality='Build Sanity - Customer Landing Page',
        title='Public customer landing page responds HTTP 200 OK',
        steps='1. Dispatch GET /; 2. Assert HTTP status code is 200.',
        inputs='GET /',
        expected_result='Landing page renders with HTTP 200 OK.',
    )
    def test_smoke_landing_page(self):
        response = self.client.get(reverse('index'))
        self.report_actual_result(f'HTTP {response.status_code}. Landing page is operational.')
        self.assertEqual(response.status_code, 200)

    @test_case(
        test_id='TC-SMK-002',
        functionality='Build Sanity - Table Menu Page',
        title='Table menu page responds HTTP 200 OK',
        steps='1. Dispatch GET /menu/<table_id>/; 2. Assert HTTP status code is 200.',
        inputs='GET /menu/61/',
        expected_result='Menu page renders with HTTP 200 OK.',
    )
    def test_smoke_menu_page(self):
        response = self.client.get(reverse('menu_page', args=[self.table.table_number]))
        self.report_actual_result(f'HTTP {response.status_code}. Menu page is operational.')
        self.assertEqual(response.status_code, 200)

    @test_case(
        test_id='TC-SMK-003',
        functionality='Build Sanity - Staff Management Dashboard',
        title='Staff dashboard management view responds HTTP 200 OK',
        steps='1. Dispatch GET /staff-dashboard/; 2. Assert HTTP status code is 200.',
        inputs='GET /staff-dashboard/',
        expected_result='Staff dashboard renders with HTTP 200 OK.',
    )
    def test_smoke_staff_dashboard(self):
        response = self.client.get(reverse('staff_dashboard'))
        self.report_actual_result(f'HTTP {response.status_code}. Staff dashboard is operational.')
        self.assertEqual(response.status_code, 200)

    @test_case(
        test_id='TC-SMK-004',
        functionality='Build Sanity - Bill & Checkout Page',
        title='Bill and checkout page responds HTTP 200 OK',
        steps='1. Dispatch GET /bill/<table_id>/; 2. Assert HTTP status code is 200.',
        inputs='GET /bill/61/',
        expected_result='Bill page renders with HTTP 200 OK.',
    )
    def test_smoke_bill_page(self):
        response = self.client.get(reverse('payment_page', args=[self.table.table_number]))
        self.report_actual_result(f'HTTP {response.status_code}. Bill page is operational.')
        self.assertEqual(response.status_code, 200)

    @test_case(
        test_id='TC-SMK-005',
        functionality='Build Sanity - Thank You Confirmation',
        title='Thank You confirmation page responds HTTP 200 OK',
        steps='1. Dispatch GET /thank-you/; 2. Assert HTTP status code is 200.',
        inputs='GET /thank-you/',
        expected_result='Thank You confirmation page renders with HTTP 200 OK.',
    )
    def test_smoke_thank_you_page(self):
        response = self.client.get(reverse('thank_you'))
        self.report_actual_result(f'HTTP {response.status_code}. Thank You page is operational.')
        self.assertEqual(response.status_code, 200)

    @test_case(
        test_id='TC-SMK-006',
        functionality='Build Sanity - Test Hub & Reports Dashboard',
        title='Automated test reports hub responds HTTP 200 OK',
        steps='1. Dispatch GET /testing/; 2. Assert HTTP status code is 200.',
        inputs='GET /testing/',
        expected_result='Test reports dashboard renders with HTTP 200 OK.',
    )
    def test_smoke_test_reports_hub(self):
        response = self.client.get(reverse('test_reports'))
        self.report_actual_result(f'HTTP {response.status_code}. Test Hub is operational.')
        self.assertEqual(response.status_code, 200)

    @test_case(
        test_id='TC-SMK-007',
        functionality='Build Sanity - Academic Methodology Guide',
        title='Academic testing methodology guide responds HTTP 200 OK',
        steps='1. Dispatch GET /testing/guide/; 2. Assert HTTP status code is 200.',
        inputs='GET /testing/guide/',
        expected_result='Testing guide documentation page renders with HTTP 200 OK.',
    )
    def test_smoke_testing_guide(self):
        response = self.client.get(reverse('testing_guide'))
        self.report_actual_result(f'HTTP {response.status_code}. Testing Guide documentation is operational.')
        self.assertEqual(response.status_code, 200)
