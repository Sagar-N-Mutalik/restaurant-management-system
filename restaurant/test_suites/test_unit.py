from types import SimpleNamespace

from django.test import SimpleTestCase

from restaurant.patterns.decorator import AddBaconDecorator, ExtraCheeseDecorator, MenuItemComponent
from restaurant.patterns.strategy import HappyHourPricing, NormalPricing, VIPDiscountPricing


class PricingStrategyTests(SimpleTestCase):
    def test_normal_price_is_unchanged(self):
        self.assertEqual(NormalPricing().calculate_final_price(10), 10)

    def test_happy_hour_applies_twenty_percent_discount(self):
        self.assertEqual(HappyHourPricing().calculate_final_price(10), 8)

    def test_vip_uses_configured_discount_rate(self):
        self.assertEqual(VIPDiscountPricing(0.9).calculate_final_price(10), 9)

    def test_gst_is_applied_to_the_provided_amount(self):
        self.assertAlmostEqual(NormalPricing().apply_gst(10), 11.8)


class CustomizationDecoratorTests(SimpleTestCase):
    def test_decorators_add_prices_and_descriptions(self):
        item = MenuItemComponent(SimpleNamespace(name='Burger', price=10))
        customized = AddBaconDecorator(ExtraCheeseDecorator(item))
        self.assertEqual(customized.get_price(), 14)
        self.assertEqual(customized.get_description(), 'Burger + Extra Cheese + Bacon')
