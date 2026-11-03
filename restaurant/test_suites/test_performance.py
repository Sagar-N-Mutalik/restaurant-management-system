from time import perf_counter

from django.test import TestCase

from restaurant.patterns.strategy import HappyHourPricing


class BoundedPerformanceTests(TestCase):
    def test_pricing_calculations_complete_within_budget(self):
        strategy = HappyHourPricing()
        started_at = perf_counter()
        for _ in range(5000):
            strategy.calculate_final_price(12.5)
        elapsed = perf_counter() - started_at
        self.assertLess(elapsed, 2.0, f'5000 pricing calculations took {elapsed:.3f}s')

    def test_landing_page_repeated_requests_complete_within_budget(self):
        started_at = perf_counter()
        for _ in range(20):
            self.assertEqual(self.client.get('/').status_code, 200)
        elapsed = perf_counter() - started_at
        self.assertLess(elapsed, 5.0, f'20 in-process page requests took {elapsed:.3f}s')
