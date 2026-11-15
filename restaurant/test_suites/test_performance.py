from time import perf_counter
from types import SimpleNamespace

from django.test import TestCase

from restaurant.models import RestaurantTable, Order, MenuItem
from restaurant.patterns.decorator import AddBaconDecorator, ExtraCheeseDecorator, MenuItemComponent
from restaurant.patterns.facade import OrderProcessingFacade
from restaurant.patterns.strategy import HappyHourPricing
from restaurant.reporting import ReportableAssertions, test_case


class BoundedPerformanceTests(ReportableAssertions, TestCase):
    @test_case(
        test_id='TC-PRF-001',
        functionality='Pricing Engine Throughput Benchmark',
        title='5,000 consecutive pricing calculations complete in under 1.0 second',
        steps='1. Loop HappyHourPricing().calculate_final_price(12.5) 5,000 times; 2. Assert elapsed time < 1.0s.',
        inputs='5,000 iterations with base price $12.50',
        expected_result='5,000 pricing operations complete in under 1.0 second (proves O(1) complexity).',
    )
    def test_pricing_calculations_complete_within_budget(self):
        strategy = HappyHourPricing()
        started_at = perf_counter()
        for _ in range(5000):
            strategy.calculate_final_price(12.5)
        elapsed = perf_counter() - started_at
        self.report_actual_result(f'5,000 pricing operations completed in {elapsed:.4f}s (Budget: <1.0s).')
        self.assertLess(elapsed, 1.0, f'5000 pricing calculations took {elapsed:.3f}s')

    @test_case(
        test_id='TC-PRF-002',
        functionality='Decorator Pattern Throughput Benchmark',
        title='2,000 dynamic topping decorator wrappings complete in under 1.0 second',
        steps='1. Loop AddBacon(ExtraCheese(Component)) 2,000 times; 2. Assert elapsed time < 1.0s.',
        inputs='2,000 iterations wrapping base item with two decorators',
        expected_result='2,000 decorator wrappings and price calculations complete in under 1.0 second.',
    )
    def test_decorator_wrapping_throughput_within_budget(self):
        started_at = perf_counter()
        for _ in range(2000):
            item = MenuItemComponent(SimpleNamespace(name='Burger', price=10.0))
            wrapped = AddBaconDecorator(ExtraCheeseDecorator(item))
            _ = wrapped.get_price()
            _ = wrapped.get_description()
        elapsed = perf_counter() - started_at
        self.report_actual_result(f'2,000 decorator wrappings completed in {elapsed:.4f}s (Budget: <1.0s).')
        self.assertLess(elapsed, 1.0, f'2000 decorator wrappings took {elapsed:.3f}s')

    @test_case(
        test_id='TC-PRF-003',
        functionality='Web Request Latency Benchmark - Home Route',
        title='20 consecutive landing page requests return HTTP 200 in under 3.0 seconds',
        steps='1. Dispatch 20 GET / requests; 2. Assert each returns HTTP 200; 3. Assert elapsed < 3.0s.',
        inputs='20 sequential GET / requests',
        expected_result='20 in-process web page dispatches complete in under 3.0 seconds.',
    )
    def test_landing_page_repeated_requests_complete_within_budget(self):
        started_at = perf_counter()
        for _ in range(20):
            self.assertEqual(self.client.get('/').status_code, 200)
        elapsed = perf_counter() - started_at
        self.report_actual_result(f'20 home page requests completed in {elapsed:.4f}s; all returned HTTP 200.')
        self.assertLess(elapsed, 3.0, f'20 in-process page requests took {elapsed:.3f}s')

    @test_case(
        test_id='TC-PRF-004',
        functionality='Web Request Latency Benchmark - Menu Route',
        title='20 consecutive menu page requests return HTTP 200 in under 3.0 seconds',
        steps='1. Dispatch 20 GET /menu/81/ requests; 2. Assert each returns HTTP 200; 3. Assert elapsed < 3.0s.',
        inputs='20 sequential GET /menu/81/ requests',
        expected_result='20 in-process menu page dispatches complete in under 3.0 seconds.',
    )
    def test_menu_page_repeated_requests_complete_within_budget(self):
        table = RestaurantTable.objects.create(table_number=81)
        started_at = perf_counter()
        for _ in range(20):
            self.assertEqual(self.client.get(f'/menu/{table.table_number}/').status_code, 200)
        elapsed = perf_counter() - started_at
        self.report_actual_result(f'20 menu page requests completed in {elapsed:.4f}s; all returned HTTP 200.')
        self.assertLess(elapsed, 3.0, f'20 menu page requests took {elapsed:.3f}s')

    @test_case(
        test_id='TC-PRF-005',
        functionality='Billing Algorithm Benchmark',
        title='20 consecutive table bill calculations complete in under 1.0 second',
        steps='1. Call calculate_table_bill 20 times for active table; 2. Assert elapsed time < 1.0s.',
        inputs='20 bill calculations on table with active order',
        expected_result='20 table billing calculations complete in under 1.0 second.',
    )
    def test_bill_calculation_repeated_runs_within_budget(self):
        table = RestaurantTable.objects.create(table_number=82)
        item = MenuItem.objects.create(name='Pizza', price=15.0, item_type='VEG')
        order = Order.objects.create(customer_name='Perf Guest', table=table, total_amount=15.0, status='PREPARING')
        order.items.add(item)

        facade = OrderProcessingFacade()
        started_at = perf_counter()
        for _ in range(20):
            bill = facade.calculate_table_bill(table.table_number)
            self.assertIsNotNone(bill)
        elapsed = perf_counter() - started_at
        self.report_actual_result(f'20 bill calculations completed in {elapsed:.4f}s (Budget: <1.0s).')
        self.assertLess(elapsed, 1.0, f'20 bill calculations took {elapsed:.3f}s')
