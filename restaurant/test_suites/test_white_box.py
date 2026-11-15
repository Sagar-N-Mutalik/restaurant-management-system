from django.test import TestCase

from restaurant.models import RestaurantTable
from restaurant.patterns.facade import OrderProcessingFacade
from restaurant.patterns.factory import (
    SimpleMenuFactory,
    VegMenuItemFactory,
    NonVegMenuItemFactory,
    VeganMenuItemFactory,
)
from restaurant.reporting import ReportableAssertions, test_case


class InternalBranchTests(ReportableAssertions, TestCase):
    @test_case(
        test_id='TC-WB-001',
        functionality='Factory Pattern - Vegetarian Concrete Creator',
        title='VegMenuItemFactory assigns item_type VEG and prepends description tag',
        steps='1. Call VegMenuItemFactory.create_item("Salad", 6.0, "Fresh greens"); 2. Assert item_type and description.',
        inputs='Name: "Salad", Price: 6.00, Description: "Fresh greens"',
        expected_result='Database object created with item_type="VEG" and description="[VEG] Fresh greens".',
    )
    def test_veg_factory_creates_veg_menu_item(self):
        item = VegMenuItemFactory.create_item('Salad', 6.0, 'Fresh greens')
        self.report_actual_result(f'Item: {item.name}, Type: {item.item_type}, Desc: {item.description}.')
        self.assertEqual(item.item_type, 'VEG')
        self.assertTrue(item.description.startswith('[VEG]'))

    @test_case(
        test_id='TC-WB-002',
        functionality='Factory Pattern - Non-Vegetarian Concrete Creator',
        title='NonVegMenuItemFactory assigns item_type NON_VEG and prepends description tag',
        steps='1. Call NonVegMenuItemFactory.create_item("Wings", 9.0, "Spicy"); 2. Assert item_type and description.',
        inputs='Name: "Wings", Price: 9.00, Description: "Spicy"',
        expected_result='Database object created with item_type="NON_VEG" and description="[NON-VEG] Spicy".',
    )
    def test_non_veg_factory_creates_non_veg_menu_item(self):
        item = NonVegMenuItemFactory.create_item('Wings', 9.0, 'Spicy')
        self.report_actual_result(f'Item: {item.name}, Type: {item.item_type}, Desc: {item.description}.')
        self.assertEqual(item.item_type, 'NON_VEG')
        self.assertTrue(item.description.startswith('[NON-VEG]'))

    @test_case(
        test_id='TC-WB-003',
        functionality='Factory Pattern - Vegan Concrete Creator',
        title='VeganMenuItemFactory assigns item_type VEGAN and prepends allergy label',
        steps='1. Call VeganMenuItemFactory.create_item("Tofu Bowl", 11.0); 2. Assert item_type and allergy notice.',
        inputs='Name: "Tofu Bowl", Price: 11.00',
        expected_result='Database object created with item_type="VEGAN" and allergy notice prefix.',
    )
    def test_vegan_factory_creates_vegan_menu_item(self):
        item = VeganMenuItemFactory.create_item('Tofu Bowl', 11.0)
        self.report_actual_result(f'Item: {item.name}, Type: {item.item_type}, Desc: {item.description}.')
        self.assertEqual(item.item_type, 'VEGAN')
        self.assertIn('[VEGAN - NO DAIRY/MEAT]', item.description)

    @test_case(
        test_id='TC-WB-004',
        functionality='Factory Pattern - Router Routing',
        title='SimpleMenuFactory correctly routes valid category strings to concrete factories',
        steps='1. Query SimpleMenuFactory with "veg", "non_veg", "vegan"; 2. Assert all created successfully.',
        inputs='Categories: "veg", "non_veg", "vegan"',
        expected_result='All valid category strings instantiate the corresponding MenuItem subclasses.',
    )
    def test_simple_menu_factory_routes_valid_categories(self):
        veg = SimpleMenuFactory.get_item('veg', 'Corn', 4.0)
        non_veg = SimpleMenuFactory.get_item('non_veg', 'Bacon Roll', 6.0)
        vegan = SimpleMenuFactory.get_item('vegan', 'Fruit Bowl', 5.0)
        self.report_actual_result(f'Routed types: {veg.item_type}, {non_veg.item_type}, {vegan.item_type}.')
        self.assertEqual(veg.item_type, 'VEG')
        self.assertEqual(non_veg.item_type, 'NON_VEG')
        self.assertEqual(vegan.item_type, 'VEGAN')

    @test_case(
        test_id='TC-WB-005',
        functionality='Factory Pattern - Unsupported Category Exception Guard',
        title='SimpleMenuFactory rejects unknown item category raising descriptive ValueError',
        steps='1. Query SimpleMenuFactory with category="invalid_type"; 2. Assert ValueError raised.',
        inputs='Category: "invalid_type"',
        expected_result='Raises ValueError: "Unknown menu item category: invalid_type".',
    )
    def test_factory_rejects_unknown_item_category(self):
        with self.assertRaisesRegex(ValueError, 'Unknown menu item category'):
            SimpleMenuFactory.get_item('invalid_type', 'Mystery', 10)
        self.report_actual_result('ValueError raised cleanly: Unknown menu item category: invalid_type.')

    @test_case(
        test_id='TC-WB-006',
        functionality='Facade Defensive Programming - Non-Existent Order',
        title='Completing an order that does not exist returns False gracefully',
        steps='1. Call OrderProcessingFacade().complete_order(99999); 2. Assert return value is False.',
        inputs='Order ID: 99999',
        expected_result='Returns False without throwing unhandled DoesNotExist exception.',
    )
    def test_completing_unknown_order_returns_false(self):
        actual = OrderProcessingFacade().complete_order(99999)
        self.report_actual_result(f'Completion result for missing order: {actual}. Handled safely.')
        self.assertFalse(actual)

    @test_case(
        test_id='TC-WB-007',
        functionality='Facade Defensive Programming - Empty Table Bill',
        title='Calculating bill for a table with no active orders returns None',
        steps='1. Create table with zero orders; 2. Call calculate_table_bill; 3. Assert return value is None.',
        inputs='Table 51 with 0 active orders',
        expected_result='Returns None cleanly, preventing zero-division or null order aggregation.',
    )
    def test_bill_for_table_without_active_orders_is_empty(self):
        table = RestaurantTable.objects.create(table_number=51)
        actual = OrderProcessingFacade().calculate_table_bill(table.table_number)
        self.report_actual_result(f'Bill for empty table: {actual}. Handled safely.')
        self.assertIsNone(actual)

    @test_case(
        test_id='TC-WB-008',
        functionality='Facade Exception Guard - Non-Existent Table Bill',
        title='Calculating bill for a table number that does not exist raises ValueError',
        steps='1. Call calculate_table_bill for Table 99999; 2. Assert ValueError raised.',
        inputs='Table number: 99999',
        expected_result='Raises ValueError: "Table 99999 does not exist.".',
    )
    def test_bill_for_nonexistent_table_raises_value_error(self):
        with self.assertRaisesRegex(ValueError, 'does not exist'):
            OrderProcessingFacade().calculate_table_bill(99999)
        self.report_actual_result('ValueError raised cleanly: Table 99999 does not exist.')

    @test_case(
        test_id='TC-WB-009',
        functionality='Facade Defensive Programming - Non-Existent Table Payment',
        title='Processing payment on a table number that does not exist returns False',
        steps='1. Call process_payment(99999); 2. Assert (False, msg) returned.',
        inputs='Table number: 99999',
        expected_result='Returns (False, "Table 99999 does not exist.") without server crash.',
    )
    def test_process_payment_on_nonexistent_table_returns_false(self):
        success, message = OrderProcessingFacade().process_payment(99999)
        self.report_actual_result(f'Success: {success}, Message: {message}.')
        self.assertFalse(success)
        self.assertIn('does not exist', message)
