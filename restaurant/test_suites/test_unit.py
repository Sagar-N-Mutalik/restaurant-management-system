from types import SimpleNamespace

from django.test import SimpleTestCase

from restaurant.patterns.decorator import AddBaconDecorator, ExtraCheeseDecorator, MenuItemComponent
from restaurant.reporting import ReportableAssertions, test_case
from restaurant.patterns.strategy import HappyHourPricing, NormalPricing, VIPDiscountPricing


class PricingStrategyTests(ReportableAssertions, SimpleTestCase):
    @test_case('Unit - Normal pricing', 'A base price of 10 remains 10.')
    def test_normal_price_is_unchanged(self):
        actual = NormalPricing().calculate_final_price(10)
        self.report_actual_result(f'Final price for base price 10: {actual}.')
        self.assertEqual(actual, 10)

    @test_case('Unit - Happy-hour pricing', 'A base price of 10 is discounted by 20% to 8.')
    def test_happy_hour_applies_twenty_percent_discount(self):
        actual = HappyHourPricing().calculate_final_price(10)
        self.report_actual_result(f'Final price for base price 10: {actual}.')
        self.assertEqual(actual, 8)

    @test_case('Unit - Configured VIP discount', 'A base price of 10 at a 90% rate becomes 9.')
    def test_vip_uses_configured_discount_rate(self):
        actual = VIPDiscountPricing(0.9).calculate_final_price(10)
        self.report_actual_result(f'Final price for base price 10: {actual}.')
        self.assertEqual(actual, 9)

    @test_case('Unit - GST calculation', 'Applying 18% GST to 10 returns 11.8.')
    def test_gst_is_applied_to_the_provided_amount(self):
        actual = NormalPricing().apply_gst(10)
        self.report_actual_result(f'Amount after GST: {actual:.2f}.')
        self.assertAlmostEqual(actual, 11.8)


class CustomizationDecoratorTests(ReportableAssertions, SimpleTestCase):
    @test_case(
        'Unit - Cheese and bacon decorators',
        'Cheese and bacon add 1.50 and 2.50, producing price 14 and the matching description.',
    )
    def test_decorators_add_prices_and_descriptions(self):
        item = MenuItemComponent(SimpleNamespace(name='Burger', price=10))
        customized = AddBaconDecorator(ExtraCheeseDecorator(item))
        actual = f'Price: {customized.get_price():.2f}; description: {customized.get_description()}.'
        self.report_actual_result(actual)
        self.assertEqual(customized.get_price(), 14)
        self.assertEqual(customized.get_description(), 'Burger + Extra Cheese + Bacon')
