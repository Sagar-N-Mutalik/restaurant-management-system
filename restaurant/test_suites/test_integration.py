from django.test import TestCase

from restaurant.models import Order, RestaurantTable, MenuItem
from restaurant.patterns.facade import OrderProcessingFacade
from restaurant.patterns.strategy import HappyHourPricing, NormalPricing
from restaurant.reporting import ReportableAssertions, test_case


class OrderWorkflowIntegrationTests(ReportableAssertions, TestCase):
    def setUp(self):
        self.table = RestaurantTable.objects.create(table_number=31)
        self.facade = OrderProcessingFacade()

    @test_case(
        test_id='TC-INT-001',
        functionality='Order Placement Workflow',
        title='Facade places order, marks table occupied, and sets status to PREPARING',
        steps='1. Create available table; 2. Call facade.place_order; 3. Query DB for Order & Table status.',
        inputs='Customer: "Integration Guest", Item: "Test Pizza", Price: 12.50, Table: 31',
        expected_result='Order is persisted with status PREPARING, table is marked occupied (is_occupied=True).',
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
            f'Order #{order.pk}: status {order.status}, total ${order.total_amount:.2f}; table occupied: {self.table.is_occupied}.'
        )
        self.assertEqual(order.status, 'PREPARING')
        self.assertEqual(order.total_amount, 12.5)
        self.assertEqual(list(order.items.values_list('name', flat=True)), ['Test Pizza'])
        self.assertTrue(self.table.is_occupied)

    @test_case(
        test_id='TC-INT-002',
        functionality='Customized Order Placement',
        title='Facade processes order with decorators and Happy-Hour strategy',
        steps='1. Call place_order with add_cheese=True, add_bacon=True, HappyHourPricing; 2. Assert price & description.',
        inputs='Base: 10.00, Extra Cheese: +1.50, Bacon: +2.50, Strategy: HappyHour (20% off total 14.00)',
        expected_result='Total price is calculated as (10 + 1.5 + 2.5) * 0.8 = 11.20 and description updated.',
    )
    def test_facade_place_order_with_decorators_and_happy_hour(self):
        result = self.facade.place_order(
            customer_name='Custom Guest',
            item_category='non_veg',
            item_name='Gourmet Burger',
            base_price=10.0,
            add_cheese=True,
            add_bacon=True,
            pricing_strategy=HappyHourPricing(),
            table_number=self.table.table_number,
        )

        order = Order.objects.get(pk=result['order_id'])
        self.report_actual_result(
            f'Order #{order.pk}: total ${order.total_amount:.2f}, description: {order.item_description}.'
        )
        self.assertEqual(float(order.total_amount), 11.20)
        self.assertIn('Extra Cheese', order.item_description)
        self.assertIn('Bacon', order.item_description)

    @test_case(
        test_id='TC-INT-003',
        functionality='Table Concurrency & Collision Guard',
        title='Facade prevents placing order on an already occupied table',
        steps='1. Occupy table by placing first order; 2. Attempt second order on same table; 3. Assert ValueError.',
        inputs='Table: 31 (occupied=True), Action: place_order() on same table',
        expected_result='System raises ValueError: "Table 31 is already occupied" preventing double booking.',
    )
    def test_facade_prevents_ordering_on_already_occupied_table(self):
        # First order occupies table
        self.facade.place_order(
            customer_name='First Guest',
            item_category='veg',
            item_name='Salad',
            base_price=5.0,
            table_number=self.table.table_number,
        )

        with self.assertRaisesRegex(ValueError, 'already occupied'):
            self.facade.place_order(
                customer_name='Intruder Guest',
                item_category='veg',
                item_name='Soup',
                base_price=4.0,
                table_number=self.table.table_number,
            )
        self.report_actual_result('ValueError raised cleanly: Table 31 is already occupied.')

    @test_case(
        test_id='TC-INT-004',
        functionality='Order State Mutation - Complete Order',
        title='Facade complete_order transitions order status to READY',
        steps='1. Place order (status PREPARING); 2. Call facade.complete_order(order_id); 3. Verify status in DB.',
        inputs='Order ID of active PREPARING order',
        expected_result='Order status transitions to READY and returns True.',
    )
    def test_facade_complete_order_transitions_state_to_ready(self):
        res = self.facade.place_order(
            customer_name='Chef Guest',
            item_category='veg',
            item_name='Paneer Tikka',
            base_price=14.0,
            table_number=self.table.table_number,
        )
        order_id = res['order_id']
        success = self.facade.complete_order(order_id)
        order = Order.objects.get(pk=order_id)
        self.report_actual_result(f'Order #{order_id} completion success: {success}, persisted status: {order.status}.')
        self.assertTrue(success)
        self.assertEqual(order.status, 'READY')

    @test_case(
        test_id='TC-INT-005',
        functionality='Table Billing Aggregation & GST',
        title='Facade calculate_table_bill aggregates multiple items and applies 18% GST',
        steps='1. Create orders with multiple items on table; 2. Call calculate_table_bill; 3. Assert subtotal and tax.',
        inputs='Table 31 with Pizza ($10.00) and Pasta ($15.00), Subtotal: $25.00, Tax: 18%',
        expected_result='Calculates raw subtotal 25.00, GST 4.50 (18%), and grand total 29.50.',
    )
    def test_facade_calculate_table_bill_aggregates_multiple_orders(self):
        item1 = MenuItem.objects.create(name='Pizza Slice', price=10.0, item_type='VEG')
        item2 = MenuItem.objects.create(name='Pasta Bowl', price=15.0, item_type='VEG')
        order = Order.objects.create(
            customer_name='Bill Guest',
            table=self.table,
            total_amount=25.0,
            status='PREPARING'
        )
        order.items.add(item1, item2)

        bill = self.facade.calculate_table_bill(self.table.table_number)
        self.report_actual_result(
            f'Table {bill["table_number"]}: subtotal ${bill["raw_subtotal"]}, GST ${bill["gst_amount"]}, grand total ${bill["grand_total"]}.'
        )
        self.assertEqual(bill['raw_subtotal'], 25.0)
        self.assertEqual(bill['gst_amount'], 4.50)
        self.assertEqual(bill['grand_total'], 29.50)

    @test_case(
        test_id='TC-INT-006',
        functionality='Payment Settlement & Table Release',
        title='Processing payment completes order, marks is_paid=True, and releases table',
        steps='1. Place order on table; 2. Call facade.process_payment; 3. Assert order paid and table available.',
        inputs='Table 31 with unpaid order',
        expected_result='Payment marks order COMPLETED and is_paid=True; table is_occupied becomes False.',
    )
    def test_payment_completes_order_and_releases_table(self):
        result = self.facade.place_order(
            customer_name='Payment Guest',
            item_category='veg',
            item_name='Test Pasta',
            base_price=10,
            table_number=self.table.table_number,
        )

        success, message = self.facade.process_payment(self.table.table_number)
        order = Order.objects.get(pk=result['order_id'])
        self.table.refresh_from_db()
        self.report_actual_result(
            f'Payment success: {success}; order paid: {order.is_paid}, status: {order.status}; table occupied: {self.table.is_occupied}.'
        )
        self.assertTrue(success)
        self.assertTrue(order.is_paid)
        self.assertEqual(order.status, 'COMPLETED')
        self.assertFalse(self.table.is_occupied)

    @test_case(
        test_id='TC-INT-007',
        functionality='Observer Event Notification Flow',
        title='Observer subsystem synchronously alerts kitchen and waitstaff upon order placement',
        steps='1. Attach tracking observer; 2. Place order via facade; 3. Assert observer received PREPARING event.',
        inputs='New Order placed for Table 31',
        expected_result='Attached observer receives status update "PREPARING" with order details.',
    )
    def test_observer_alert_flow_on_order_placement(self):
        notifications = []

        class TestAuditObserver:
            def update(self, order):
                notifications.append((order.id, order.status))

        audit_observer = TestAuditObserver()
        self.facade.order_subject.attach(audit_observer)

        try:
            res = self.facade.place_order(
                customer_name='Alert Guest',
                item_category='veg',
                item_name='Nachos',
                base_price=8.0,
                table_number=self.table.table_number,
            )
            self.report_actual_result(f'Notifications captured: {notifications}.')
            self.assertTrue(any(status == 'PREPARING' for _, status in notifications))
        finally:
            self.facade.order_subject.detach(audit_observer)
