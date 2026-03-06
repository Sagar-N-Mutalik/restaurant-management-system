"""
Facade Design Pattern Implementation

Pattern Goal: Provide a unified, overarching interface to a set of interfaces in a complex subsystem. 
Facade defines a higher-level gateway that makes the sprawling subsystem dramatically easier to use.

Real-world Problem Solved:
Our Django API views run the huge risk of becoming overly bloated if they have to interact directly with 
all the isolated sub-patterns: communicating with the Factory (to instantiate items), calling Decorators 
(to add complex customizations repeatedly), leveraging Strategy (to apply conditional billing rules), and 
calling the Observer subject (to push asynchronous notifications). A view's solitary job dictates that 
it should handle an HTTP request/response efficiently—not to manually orchestrate internal domain actions step-by-step.

How it implements the pattern:
The `OrderProcessingFacade` acts as our orchestration layer managing all shifting parts. 
It exposes incredibly simple, high-level structural methods (`place_order`, `complete_order`) strictly aimed at 
the Django `views.py`. Intricate subsystem complexities (dynamic instantiation, mathematical calculus strategy, 
attaching event observers recursively, and updating DB states) are carefully hidden behind this robust exterior wall. 
The views themselves act merely as thin clients invoking this simplified facade wrapper.
"""

from restaurant.models import Order, RestaurantTable
from restaurant.patterns.factory import SimpleMenuFactory
from restaurant.patterns.decorator import MenuItemComponent, ExtraCheeseDecorator, AddBaconDecorator
from restaurant.patterns.strategy import PricingStrategy, NormalPricing
from restaurant.patterns.observer import OrderSubject, KitchenDisplayNotifier, WaiterNotifier

class OrderProcessingFacade:
    """
    Facade class shielding the thin view client from the expansive patterns subsystem architecture.
    """
    def __init__(self):
        # Set up the event notification subsystem natively (Observer)
        self.order_subject = OrderSubject()
        
        # Instantiate and Attach concrete UI/Hardware observers
        self.kitchen_display = KitchenDisplayNotifier()
        self.waiter_notifier = WaiterNotifier()
        
        self.order_subject.attach(self.kitchen_display)
        self.order_subject.attach(self.waiter_notifier)

    def place_order(self, customer_name: str, item_category: str, item_name: str, base_price: float, 
                    add_cheese: bool = False, add_bacon: bool = False, 
                    pricing_strategy: PricingStrategy = None, table_number: int = None):
        """
        A unified macro method to process an order end-to-end heavily utilizing all sub-patterns.
        """
        # Resolve Strategy Pattern (default to Normal) if practically omitted
        if pricing_strategy is None:
            pricing_strategy = NormalPricing()

        # Step 1: Encapsulate Factory implementation to build the core ORM object safely
        base_item = SimpleMenuFactory.get_item(
            item_category=item_category,
            name=item_name,
            price=base_price
        )

        # Step 2: Use Decorator to wrap the database item with temporary in-memory customizations flexibly
        item_component = MenuItemComponent(base_item)
        if add_cheese:
            item_component = ExtraCheeseDecorator(item_component)
        if add_bacon:
            item_component = AddBaconDecorator(item_component)

        # Extract base customized raw cost dynamically from the wrappers
        raw_cost = item_component.get_price()
        final_description = item_component.get_description()

        # Step 3: Apply Strategy Pattern blindly to extract the perfectly calculated final price
        final_price = pricing_strategy.calculate_final_price(raw_cost)

        # Locate the table if provided
        table = None
        if table_number:
            table = RestaurantTable.objects.filter(table_number=table_number).first()
            if not table:
                raise ValueError(f"Table {table_number} does not exist.")
            if table.is_occupied:
                raise ValueError(f"Table {table_number} is already occupied.")

        # Step 4: Persist the finalized order explicitly to the core Database
        order = Order.objects.create(
            customer_name=customer_name,
            table=table,
            total_amount=final_price,
            status='PENDING',
            item_description=final_description
        )
        order.items.add(base_item)

        # Update table status
        if table:
            table.is_occupied = True
            table.save()

        # Step 5: Trigger Observer Pattern events natively pushing the alert to systems decoupled
        self.order_subject.change_order_status(order, 'PREPARING')

        # Deliver a sanitized, concise payload outwards to the client view wrapper
        return {
            'order_id': order.id,
            'customer': order.customer_name,
            'table_number': table.table_number if table else None,
            'item_description': final_description,
            'final_price': final_price,
            'status': order.status
        }
    
    def complete_order(self, order_id: int):
        """
        Macro method to transition a historical order immediately to READY. 
        It safely sparks the waitstaff observer notifications.
        """
        try:
            order = Order.objects.get(id=order_id)
            self.order_subject.change_order_status(order, 'READY')
            return True
        except Order.DoesNotExist:
            return False

    def process_payment(self, table_number: int):
        """
        Macro method that finalizes the order and frees up the physical table for the next customers.
        Supports processing multiple active orders on a single table.
        """
        try:
            table = RestaurantTable.objects.get(table_number=table_number)
            # Fetch all active unpaid orders for this table
            orders = Order.objects.filter(table=table, is_paid=False).exclude(status='COMPLETED')
            
            if not orders.exists():
                return False, f"No active unpaid order found for Table {table_number}."
            
            # Change State for all orders
            for order in orders:
                order.is_paid = True
                order.status = 'COMPLETED'
                order.save()

            table.is_occupied = False
            table.save()

            return True, f"Payment successfully processed. Table {table_number} is now available."
            
        except RestaurantTable.DoesNotExist:
            return False, f"Table {table_number} does not exist."

    def calculate_table_bill(self, table_number: int, pricing_strategy: PricingStrategy = None):
        """
        Dynamically aggregates all active orders for a single table, computes the combined
        subtotal using the provided Strategy Pattern, applies GST natively, and returns an itemized bill.
        """
        if pricing_strategy is None:
            pricing_strategy = NormalPricing()
            
        try:
            table = RestaurantTable.objects.get(table_number=table_number)
            orders = Order.objects.filter(table=table, is_paid=False).exclude(status='COMPLETED')
            
            if not orders.exists():
                return None
                
            itemized_list = []
            raw_subtotal = 0.0
            order_ids = []
            
            # Aggregate all order items dynamically
            for order in orders:
                order_ids.append(order.id)
                for item in order.items.all():
                    # For simplicity, we are capturing the raw base price. 
                    # If Decorators were saved statically, their customized cost would apply here.
                    itemized_list.append({
                        'name': item.name,
                        'price': float(item.price)
                    })
                    raw_subtotal += float(item.price)
                    
            # 1. Apply Discount Strategy
            discounted_subtotal = pricing_strategy.calculate_final_price(raw_subtotal)
            discount_applied = raw_subtotal - discounted_subtotal
            
            # 2. Apply 18% GST (Tax Strategy)
            grand_total = pricing_strategy.apply_gst(discounted_subtotal)
            gst_amount = grand_total - discounted_subtotal
            
            return {
                'table_number': table.table_number,
                'order_ids': order_ids,
                'itemized_list': itemized_list,
                'raw_subtotal': round(raw_subtotal, 2),
                'discount_applied': round(discount_applied, 2),
                'subtotal_after_discount': round(discounted_subtotal, 2),
                'gst_amount': round(gst_amount, 2),
                'grand_total': round(grand_total, 2)
            }

        except RestaurantTable.DoesNotExist:
            raise ValueError(f"Table {table_number} does not exist.")
