import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from restaurant.models import Order, RestaurantTable, MenuItem
from restaurant.patterns.facade import OrderProcessingFacade
from restaurant.patterns.strategy import HappyHourPricing, NormalPricing
from restaurant.reporting import ReportableAssertions, test_case


class OrderRegressionTests(ReportableAssertions, TestCase):
    @test_case(
        test_id='TC-REG-001',
        functionality='Input Validation - Corrupted JSON Payload',
        title='Malformed JSON order request safely returns HTTP 400 Bad Request',
        steps='1. POST /api/order with data="{invalid"; 2. Assert HTTP 400 and success: false.',
        inputs='Malformed JSON string "{invalid"',
        expected_result='HTTP 400 Bad Request with JSON {"success": false, "error": ...}.',
    )
    def test_invalid_json_order_request_returns_bad_request(self):
        response = self.client.post(
            reverse('api_create_order'),
            data='{invalid',
            content_type='application/json',
        )
        self.report_actual_result(f'HTTP {response.status_code}; success: {response.json().get("success")}. Handled safely.')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    @test_case(
        test_id='TC-REG-002',
        functionality='Input Validation - Empty Order Payload',
        title='Empty request payload in order API returns HTTP 400 Bad Request',
        steps='1. POST /api/order with data="{}"; 2. Assert HTTP 400 Bad Request.',
        inputs='Empty JSON object "{}"',
        expected_result='HTTP 400 Bad Request with failure notice.',
    )
    def test_empty_order_payload_returns_bad_request(self):
        response = self.client.post(
            reverse('api_create_order'),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.report_actual_result(f'HTTP {response.status_code}; success: {response.json().get("success")}.')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    @test_case(
        test_id='TC-REG-003',
        functionality='State Machine - Ready Status Transition',
        title='Order ready API updates order status and persists in database',
        steps='1. Create order; 2. POST /api/order/<id>/ready; 3. Assert HTTP 200 and DB status READY.',
        inputs='Order ID of active order',
        expected_result='HTTP 200 OK and database record status is updated to READY.',
    )
    def test_ready_endpoint_updates_order_state(self):
        table = RestaurantTable.objects.create(table_number=71)
        result = OrderProcessingFacade().place_order(
            customer_name='Ready Guest',
            item_category='veg',
            item_name='Ready Pizza',
            base_price=10,
            table_number=table.table_number,
        )
        with patch('builtins.print'):
            response = self.client.post(
                reverse('api_order_ready', args=[result['order_id']]),
                data=json.dumps({}),
                content_type='application/json',
            )
        order = Order.objects.get(pk=result['order_id'])
        self.report_actual_result(
            f'HTTP {response.status_code}; response success: {response.json().get("success")}; persisted status: {order.status}.'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(order.status, 'READY')

    @test_case(
        test_id='TC-REG-004',
        functionality='State Machine - Missing Order Ready Guard',
        title='Ready endpoint for non-existent order returns HTTP 404 cleanly',
        steps='1. POST /api/order/99999/ready; 2. Assert HTTP 404 Not Found.',
        inputs='Non-existent order ID: 99999',
        expected_result='HTTP 404 with JSON {"success": false, "error": ...}.',
    )
    def test_ready_endpoint_missing_order_returns_404(self):
        response = self.client.post(
            reverse('api_order_ready', args=[99999]),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.report_actual_result(f'HTTP {response.status_code}; error: {response.json().get("error")}.')
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()['success'])

    @test_case(
        test_id='TC-REG-005',
        functionality='Payment Idempotence - Empty Table Payment Guard',
        title='Attempting payment on table with no unpaid orders fails safely',
        steps='1. Create occupied table with 0 orders; 2. Process payment; 3. Assert False and table remains occupied.',
        inputs='Occupied Table 72 with zero active orders',
        expected_result='Payment returns False without clearing table occupancy.',
    )
    def test_failed_payment_keeps_table_occupied(self):
        table = RestaurantTable.objects.create(table_number=72, is_occupied=True)
        success, message = OrderProcessingFacade().process_payment(table.table_number)
        table.refresh_from_db()
        self.report_actual_result(f'Payment success: {success}; table occupied: {table.is_occupied}; message: {message}.')
        self.assertFalse(success)
        self.assertTrue(table.is_occupied)

    @test_case(
        test_id='TC-REG-006',
        functionality='Payment Idempotence - Missing Table Payment Guard',
        title='Payment processing for non-existent table number returns error without 500 crash',
        steps='1. POST /payment/99999/process/; 2. Assert HTTP 400 Bad Request.',
        inputs='Non-existent table number: 99999',
        expected_result='HTTP 400 Bad Request with error description.',
    )
    def test_payment_for_nonexistent_table_returns_bad_request(self):
        response = self.client.post(reverse('process_payment', args=[99999]))
        self.report_actual_result(f'HTTP {response.status_code}; error: {response.json().get("error")}.')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    @test_case(
        test_id='TC-REG-007',
        functionality='Pricing Isolation - Cart Items Independence',
        title='Multi-item cart computes individual item prices without state bleeding',
        steps='1. Submit cart with Happy-Hour item ($10 -> $8) and Normal item ($20 -> $20); 2. Assert individual prices.',
        inputs='Item 1: $10 (HappyHour), Item 2: $20 (Normal)',
        expected_result='Order 1 is charged 8.00 and Order 2 is charged 20.00 independently.',
    )
    def test_multi_item_order_pricing_integrity(self):
        table = RestaurantTable.objects.create(table_number=73)
        response = self.client.post(
            reverse('api_create_order'),
            data=json.dumps({
                'table_number': table.table_number,
                'customer_name': 'Cart Isolation Guest',
                'items': [
                    {'item_name': 'Item A', 'price': 10.0, 'category': 'veg', 'strategy': 'happy_hour'},
                    {'item_name': 'Item B', 'price': 20.0, 'category': 'veg', 'strategy': 'normal'},
                ]
            }),
            content_type='application/json',
        )
        orders = response.json()['orders']
        self.report_actual_result(f'Order 1: ${orders[0]["final_price"]}, Order 2: ${orders[1]["final_price"]}.')
        self.assertEqual(orders[0]['final_price'], 8.0)
        self.assertEqual(orders[1]['final_price'], 20.0)

    @test_case(
        test_id='TC-REG-008',
        functionality='Bill Mathematics - Mathematical Integrity',
        title='Table bill calculation preserves mathematical equality: subtotal + GST == grand_total',
        steps='1. Create orders on table; 2. Calculate bill; 3. Assert subtotal_after_discount + gst == grand_total.',
        inputs='Table 74 with multiple items',
        expected_result='Mathematical identity subtotal_after_discount + gst_amount == grand_total holds exactly.',
    )
    def test_table_bill_reflects_discount_and_gst_accurately(self):
        table = RestaurantTable.objects.create(table_number=74)
        item = MenuItem.objects.create(name='Steak', price=50.0, item_type='NON_VEG')
        order = Order.objects.create(customer_name='Math Guest', table=table, total_amount=50.0, status='PREPARING')
        order.items.add(item)

        bill = OrderProcessingFacade().calculate_table_bill(table.table_number, pricing_strategy=HappyHourPricing())
        # Subtotal: 50.0 -> HappyHour (20% off) = 40.0. GST (18%) = 7.20. Grand Total = 47.20.
        self.report_actual_result(
            f'Subtotal: ${bill["subtotal_after_discount"]}, GST: ${bill["gst_amount"]}, Grand Total: ${bill["grand_total"]}.'
        )
        self.assertEqual(bill['subtotal_after_discount'], 40.0)
        self.assertEqual(bill['gst_amount'], 7.20)
        self.assertEqual(bill['grand_total'], 47.20)
        self.assertAlmostEqual(bill['subtotal_after_discount'] + bill['gst_amount'], bill['grand_total'])
