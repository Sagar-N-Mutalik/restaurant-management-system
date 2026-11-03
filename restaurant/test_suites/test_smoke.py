from django.test import TestCase
from django.urls import reverse

from restaurant.models import RestaurantTable


class MainPageSmokeTests(TestCase):
    def test_main_pages_load(self):
        table = RestaurantTable.objects.create(table_number=61)
        routes = (
            reverse('index'),
            reverse('staff_dashboard'),
            reverse('test_reports'),
            reverse('menu_page', args=[table.table_number]),
            reverse('payment_page', args=[table.table_number]),
        )
        for route in routes:
            with self.subTest(route=route):
                self.assertEqual(self.client.get(route).status_code, 200)
