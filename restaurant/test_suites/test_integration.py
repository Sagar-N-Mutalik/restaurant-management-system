from django.test import TestCase

from restaurant.models import Order, RestaurantTable
from restaurant.patterns.facade import OrderProcessingFacade
from restaurant.patterns.strategy import NormalPricing


class OrderWorkflowIntegrationTests(TestCase):
    def setUp(self):
        self.table = RestaurantTable.objects.create(table_number=31)
        self.facade = OrderProcessingFacade()

    def test_facade_persists_order_and_occupies_table(self):
        result = self.facade.place_order(
            customer_name='Integration Guest',
            item_category='veg',
            item_name='Test Pizza',
            base_price=12.5,
            pricing_strategy=NormalPricing(),
            table_number=self.table.table_number,
        )

        order = Order.objects.get(pk=result['order_id'])
        self.table.refresh_from_db()
        self.assertEqual(order.status, 'PREPARING')
        self.assertEqual(order.total_amount, 12.5)
        self.assertEqual(list(order.items.values_list('name', flat=True)), ['Test Pizza'])
        self.assertTrue(self.table.is_occupied)

    def test_payment_completes_order_and_releases_table(self):
        result = self.facade.place_order(
            customer_name='Payment Guest',
            item_category='veg',
            item_name='Test Pasta',
            base_price=10,
            table_number=self.table.table_number,
        )

        success, _ = self.facade.process_payment(self.table.table_number)
        order = Order.objects.get(pk=result['order_id'])
        self.table.refresh_from_db()
        self.assertTrue(success)
        self.assertTrue(order.is_paid)
        self.assertEqual(order.status, 'COMPLETED')
        self.assertFalse(self.table.is_occupied)
