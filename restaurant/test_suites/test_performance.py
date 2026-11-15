from time import perf_counter

from django.test import TestCase

from restaurant.reporting import ReportableAssertions, test_case
from restaurant.patterns.strategy import HappyHourPricing


class BoundedPerformanceTests(ReportableAssertions, TestCase):
    @test_case('Performance - Pricing calculations', '5,000 pricing calculations complete in under 2 seconds.')
    def test_pricing_calculations_complete_within_budget(self):
        strategy = HappyHourPricing()
        started_at = perf_counter()
        for _ in range(5000):
            strategy.calculate_final_price(12.5)
        elapsed = perf_counter() - started_at
        self.report_actual_result(f'5,000 pricing calculations completed in {elapsed:.4f} seconds.')
        self.assertLess(elapsed, 2.0, f'5000 pricing calculations took {elapsed:.3f}s')

    @test_case('Performance - Home page response', '20 in-process home page requests return HTTP 200 in under 5 seconds.')
    def test_landing_page_repeated_requests_complete_within_budget(self):
        started_at = perf_counter()
        for _ in range(20):
            self.assertEqual(self.client.get('/').status_code, 200)
        elapsed = perf_counter() - started_at
        self.report_actual_result(f'20 home page requests completed in {elapsed:.4f} seconds; all returned HTTP 200.')
        self.assertLess(elapsed, 5.0, f'20 in-process page requests took {elapsed:.3f}s')
