import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from restaurant.models import Order, RestaurantTable
from restaurant.patterns.facade import OrderProcessingFacade


class OrderRegressionTests(TestCase):
    def test_invalid_json_order_request_returns_bad_request(self):
        response = self.client.post(
            reverse('api_create_order'),
            data='{invalid',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

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
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(order.status, 'READY')

    def test_failed_payment_keeps_table_occupied(self):
        table = RestaurantTable.objects.create(table_number=72, is_occupied=True)
        success, _ = OrderProcessingFacade().process_payment(table.table_number)
        table.refresh_from_db()
        self.assertFalse(success)
        self.assertTrue(table.is_occupied)
