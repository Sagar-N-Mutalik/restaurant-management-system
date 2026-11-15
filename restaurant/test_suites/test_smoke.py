from django.test import TestCase
from django.urls import reverse

from restaurant.models import RestaurantTable
from restaurant.reporting import ReportableAssertions, test_case


class MainPageSmokeTests(ReportableAssertions, TestCase):
    @test_case('Smoke - Main pages load', 'Home, staff dashboard, reports, menu, and payment routes return HTTP 200.')
    def test_main_pages_load(self):
        table = RestaurantTable.objects.create(table_number=61)
        routes = (
            reverse('index'),
            reverse('staff_dashboard'),
            reverse('test_reports'),
            reverse('menu_page', args=[table.table_number]),
            reverse('payment_page', args=[table.table_number]),
        )
        statuses = [(route, self.client.get(route).status_code) for route in routes]
        self.report_actual_result('; '.join(f'{route}: HTTP {status}' for route, status in statuses))
        for route, status in statuses:
            with self.subTest(route=route):
                self.assertEqual(status, 200)
