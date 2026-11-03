from django.test import TestCase

from restaurant.models import RestaurantTable
from restaurant.patterns.facade import OrderProcessingFacade
from restaurant.patterns.factory import SimpleMenuFactory


class InternalBranchTests(TestCase):
    def test_factory_rejects_unknown_item_category(self):
        with self.assertRaisesRegex(ValueError, 'Unknown menu item category'):
            SimpleMenuFactory.get_item('unknown', 'Mystery', 10)

    def test_completing_unknown_order_returns_false(self):
        self.assertFalse(OrderProcessingFacade().complete_order(99999))

    def test_bill_for_table_without_active_orders_is_empty(self):
        table = RestaurantTable.objects.create(table_number=51)
        self.assertIsNone(OrderProcessingFacade().calculate_table_bill(table.table_number))
