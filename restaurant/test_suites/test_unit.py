from types import SimpleNamespace
from django.test import SimpleTestCase

from restaurant.patterns.decorator import AddBaconDecorator, ExtraCheeseDecorator, MenuItemComponent
from restaurant.patterns.observer import OrderSubject, OrderObserver
from restaurant.patterns.singleton import RestaurantConfigManager
from restaurant.patterns.strategy import HappyHourPricing, NormalPricing, VIPDiscountPricing
from restaurant.reporting import ReportableAssertions, test_case


class PricingStrategyTests(ReportableAssertions, SimpleTestCase):
    @test_case(
        test_id='TC-UNIT-001',
        functionality='Pricing Strategy - Normal Pricing',
        title='Normal pricing preserves base item price',
        steps='1. Instantiate NormalPricing; 2. Call calculate_final_price(100.0); 3. Verify price remains 100.0.',
        inputs='Base price: 100.00, Strategy: NormalPricing',
        expected_result='A base price of 100.00 remains exactly 100.00 without alteration.',
    )
    def test_normal_price_is_unchanged(self):
        actual = NormalPricing().calculate_final_price(100.0)
        self.report_actual_result(f'Final calculated price: {actual:.2f}. Matches expected base price.')
        self.assertEqual(actual, 100.0)

    @test_case(
        test_id='TC-UNIT-002',
        functionality='Pricing Strategy - Happy Hour Discount',
        title='Happy-hour pricing applies exactly 20% discount',
        steps='1. Instantiate HappyHourPricing; 2. Call calculate_final_price(100.0); 3. Verify price becomes 80.0.',
        inputs='Base price: 100.00, Strategy: HappyHourPricing (0.8x multiplier)',
        expected_result='A base price of 100.00 is discounted by 20% to return exactly 80.00.',
    )
    def test_happy_hour_applies_twenty_percent_discount(self):
        actual = HappyHourPricing().calculate_final_price(100.0)
        self.report_actual_result(f'Final calculated price: {actual:.2f}. 20% discount verified.')
        self.assertEqual(actual, 80.0)

    @test_case(
        test_id='TC-UNIT-003',
        functionality='Pricing Strategy - VIP Default Discount',
        title='VIP pricing applies default 30% discount',
        steps='1. Instantiate VIPDiscountPricing(); 2. Call calculate_final_price(100.0); 3. Verify price is 70.0.',
        inputs='Base price: 100.00, Strategy: VIPDiscountPricing (default 0.7x multiplier)',
        expected_result='A base price of 100.00 is discounted by 30% to return exactly 70.00.',
    )
    def test_vip_uses_default_discount_rate(self):
        actual = VIPDiscountPricing().calculate_final_price(100.0)
        self.report_actual_result(f'Final calculated price: {actual:.2f}. Default 30% VIP discount verified.')
        self.assertEqual(actual, 70.0)

    @test_case(
        test_id='TC-UNIT-004',
        functionality='Pricing Strategy - VIP Custom Discount',
        title='VIP pricing applies configured custom rate',
        steps='1. Instantiate VIPDiscountPricing(0.85); 2. Call calculate_final_price(100.0); 3. Verify price is 85.0.',
        inputs='Base price: 100.00, Custom Rate: 0.85 (15% discount)',
        expected_result='A base price of 100.00 at an 85% rate returns exactly 85.00.',
    )
    def test_vip_uses_configured_discount_rate(self):
        actual = VIPDiscountPricing(0.85).calculate_final_price(100.0)
        self.report_actual_result(f'Final calculated price: {actual:.2f}. Custom VIP rate 0.85 verified.')
        self.assertEqual(actual, 85.0)

    @test_case(
        test_id='TC-UNIT-005',
        functionality='Tax Calculation - 18% GST',
        title='18% GST tax calculation is mathematically exact',
        steps='1. Instantiate NormalPricing; 2. Call apply_gst(100.0); 3. Verify amount is 118.0.',
        inputs='Subtotal amount: 100.00, GST Rate: 18%',
        expected_result='Applying 18% GST to 100.00 returns exactly 118.00.',
    )
    def test_gst_is_applied_to_the_provided_amount(self):
        actual = NormalPricing().apply_gst(100.0)
        self.report_actual_result(f'Final total after 18% GST: {actual:.2f}.')
        self.assertAlmostEqual(actual, 118.0)


class CustomizationDecoratorTests(ReportableAssertions, SimpleTestCase):
    @test_case(
        test_id='TC-UNIT-006',
        functionality='Decorator Pattern - Extra Cheese',
        title='Extra cheese decorator adds $1.50 and updates description',
        steps='1. Create MenuItemComponent("Pizza", 12.0); 2. Wrap with ExtraCheeseDecorator; 3. Assert price and name.',
        inputs='Item: Pizza ($12.00), Decorator: ExtraCheeseDecorator (+$1.50)',
        expected_result='Price becomes 13.50 and description becomes "Pizza + Extra Cheese".',
    )
    def test_extra_cheese_decorator(self):
        item = MenuItemComponent(SimpleNamespace(name='Pizza', price=12.0))
        customized = ExtraCheeseDecorator(item)
        self.report_actual_result(f'Price: {customized.get_price():.2f}, Description: {customized.get_description()}.')
        self.assertEqual(customized.get_price(), 13.50)
        self.assertEqual(customized.get_description(), 'Pizza + Extra Cheese')

    @test_case(
        test_id='TC-UNIT-007',
        functionality='Decorator Pattern - Add Bacon',
        title='Add bacon decorator adds $2.50 and updates description',
        steps='1. Create MenuItemComponent("Burger", 10.0); 2. Wrap with AddBaconDecorator; 3. Assert price and name.',
        inputs='Item: Burger ($10.00), Decorator: AddBaconDecorator (+$2.50)',
        expected_result='Price becomes 12.50 and description becomes "Burger + Bacon".',
    )
    def test_add_bacon_decorator(self):
        item = MenuItemComponent(SimpleNamespace(name='Burger', price=10.0))
        customized = AddBaconDecorator(item)
        self.report_actual_result(f'Price: {customized.get_price():.2f}, Description: {customized.get_description()}.')
        self.assertEqual(customized.get_price(), 12.50)
        self.assertEqual(customized.get_description(), 'Burger + Bacon')

    @test_case(
        test_id='TC-UNIT-008',
        functionality='Decorator Pattern - Multiple Topping Chaining',
        title='Multiple chained decorators dynamically aggregate prices and descriptions',
        steps='1. Create base Burger ($10.0); 2. Wrap with ExtraCheese then AddBacon; 3. Assert price is 14.0.',
        inputs='Base: Burger ($10.00), Decorators: ExtraCheese ($1.50) + AddBacon ($2.50)',
        expected_result='Decorators stack cumulatively, producing total price 14.00 and concatenated name.',
    )
    def test_decorators_add_prices_and_descriptions(self):
        item = MenuItemComponent(SimpleNamespace(name='Burger', price=10.0))
        customized = AddBaconDecorator(ExtraCheeseDecorator(item))
        actual = f'Price: {customized.get_price():.2f}; Description: {customized.get_description()}'
        self.report_actual_result(actual)
        self.assertEqual(customized.get_price(), 14.0)
        self.assertEqual(customized.get_description(), 'Burger + Extra Cheese + Bacon')


class ArchitecturalPatternUnitTests(ReportableAssertions, SimpleTestCase):
    @test_case(
        test_id='TC-UNIT-009',
        functionality='Singleton Pattern - Instance Identity',
        title='RestaurantConfigManager enforces a single object instance in memory',
        steps='1. Instantiate config1 = RestaurantConfigManager(); 2. Instantiate config2; 3. Assert config1 is config2.',
        inputs='Multiple instantiations of RestaurantConfigManager()',
        expected_result='Both references point to the exact same object in memory (id(config1) == id(config2)).',
    )
    def test_singleton_config_manager_single_instance(self):
        config1 = RestaurantConfigManager()
        config2 = RestaurantConfigManager()
        self.report_actual_result(f'config1 (id {id(config1)}) is config2 (id {id(config2)}): {config1 is config2}.')
        self.assertIs(config1, config2)

    @test_case(
        test_id='TC-UNIT-010',
        functionality='Singleton Pattern - State Mutation Persistence',
        title='Modifying configuration settings on one reference persists globally',
        steps='1. Update tax rate via config1.update_tax_rate(0.12); 2. Query config2.get_tax_rate(); 3. Assert 0.12.',
        inputs='New tax rate: 0.12 (12%)',
        expected_result='All components querying config manager observe the updated 12% tax rate.',
    )
    def test_singleton_config_manager_tax_rate_persistence(self):
        config1 = RestaurantConfigManager()
        original_rate = config1.get_tax_rate()
        try:
            config1.update_tax_rate(0.12)
            config2 = RestaurantConfigManager()
            self.report_actual_result(f'config2 retrieved updated tax rate: {config2.get_tax_rate():.2f}.')
            self.assertEqual(config2.get_tax_rate(), 0.12)
        finally:
            config1.update_tax_rate(original_rate)

    @test_case(
        test_id='TC-UNIT-011',
        functionality='Observer Pattern - Subject Registration',
        title='OrderSubject registers and detaches observers correctly',
        steps='1. Create OrderSubject; 2. Attach concrete observer; 3. Assert in list; 4. Detach observer; 5. Assert removed.',
        inputs='Subject: OrderSubject, Observer: DummyOrderObserver',
        expected_result='Observer is cleanly registered to the subject and unsubscribed on detach.',
    )
    def test_observer_subject_attach_and_detach(self):
        class DummyObserver(OrderObserver):
            def update(self, order, new_status):
                pass

        subject = OrderSubject()
        observer = DummyObserver()
        subject.attach(observer)
        self.assertIn(observer, subject._observers)
        subject.detach(observer)
        self.assertNotIn(observer, subject._observers)
        self.report_actual_result('Observer successfully attached and detached from subject list.')
