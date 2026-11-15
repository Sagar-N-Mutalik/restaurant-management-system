from django.test import TestCase

from restaurant.models import Order, RestaurantTable
from restaurant.patterns.facade import OrderProcessingFacade
from restaurant.reporting import ReportableAssertions, test_case
from restaurant.patterns.strategy import NormalPricing


class OrderWorkflowIntegrationTests(ReportableAssertions, TestCase):
    def setUp(self):
        self.table = RestaurantTable.objects.create(table_number=31)
        self.facade = OrderProcessingFacade()

    @test_case(
        'Integration - Place order',
        'Order is saved with the requested item and price, enters PREPARING, and occupies its table.',
    )
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
        self.report_actual_result(
            f'Order #{order.pk}: status {order.status}, total {order.total_amount}, '
            f'items {list(order.items.values_list("name", flat=True))}; table occupied: {self.table.is_occupied}.'
        )
        self.assertEqual(order.status, 'PREPARING')
        self.assertEqual(order.total_amount, 12.5)
        self.assertEqual(list(order.items.values_list('name', flat=True)), ['Test Pizza'])
        self.assertTrue(self.table.is_occupied)

    @test_case(
        'Integration - Process payment',
        'Payment marks the order paid and COMPLETED, then releases the table.',
    )
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
        self.report_actual_result(
            f'Payment success: {success}; order paid: {order.is_paid}, status: {order.status}; '
            f'table occupied: {self.table.is_occupied}.'
        )
        self.assertTrue(success)
        self.assertTrue(order.is_paid)
        self.assertEqual(order.status, 'COMPLETED')
        self.assertFalse(self.table.is_occupied)
