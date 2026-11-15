from django.test import TestCase

from restaurant.models import RestaurantTable
from restaurant.patterns.facade import OrderProcessingFacade
from restaurant.patterns.factory import SimpleMenuFactory
from restaurant.reporting import ReportableAssertions, test_case


class InternalBranchTests(ReportableAssertions, TestCase):
    @test_case(
        'White-box - Unknown menu category',
        'An unsupported menu category raises ValueError with an explanatory message.',
    )
    def test_factory_rejects_unknown_item_category(self):
        with self.assertRaisesRegex(ValueError, 'Unknown menu item category'):
            SimpleMenuFactory.get_item('unknown', 'Mystery', 10)
        self.report_actual_result('ValueError raised: Unknown menu item category: unknown.')

    @test_case('White-box - Missing order', 'Completing an order that does not exist returns False.')
    def test_completing_unknown_order_returns_false(self):
        actual = OrderProcessingFacade().complete_order(99999)
        self.report_actual_result(f'Completion result for missing order: {actual}.')
        self.assertFalse(actual)

    @test_case('White-box - Empty table bill', 'A table with no active orders has no bill (None).')
    def test_bill_for_table_without_active_orders_is_empty(self):
        table = RestaurantTable.objects.create(table_number=51)
        actual = OrderProcessingFacade().calculate_table_bill(table.table_number)
        self.report_actual_result(f'Bill for empty table: {actual}.')
        self.assertIsNone(actual)
