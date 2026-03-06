"""
Observer Design Pattern Implementation

Pattern Goal: Define a one-to-many dependency between objects so that when one object changes 
state, all its dependents are notified and updated automatically.

Real-world Problem Solved:
When a customer's order is placed or its status transitions (e.g., from 'Pending' to 'Preparing', or 'Ready'), 
multiple diverse systems need to react. The kitchen display needs to pop up the order, the waiter's tablet
needs an alert to pick it up later, and potentially third party delivery APIs need triggering. 
If the Order logic class directly calls these distinct systems inline `if status == 'Ready': waiter.alert()`, 
it becomes highly coupled and hard to maintain as new alert systems are arbitrarily added over time.

How it implements the pattern:
We perfectly decouple the notification logic from the state-changing logic. The `OrderSubject` ( Publisher / Subject ) 
tracks a list of event subscribers (`OrderObserver` interface clients). When an order's state actively changes, 
the subject loops over its anonymous subscribers and triggers their `update(order)` method. 
The `KitchenDisplayNotifier` and `WaiterNotifier` are concrete observers that process independently 
how they visibly react, shielding the core system from implementation details.
"""

from abc import ABC, abstractmethod
from typing import List
from restaurant.models import Order

class OrderObserver(ABC):
    """
    The Observer interface declaring the universally expected update method.
    """
    @abstractmethod
    def update(self, order: Order):
        pass


class KitchenDisplayNotifier(OrderObserver):
    """
    Concrete Observer: Notifies the kitchen display seamlessly when an order is Placed/Preparing.
    """
    def update(self, order: Order):
        print(f"\n[KITCHEN DISPLAY] Alert: Order #{order.id} for {order.customer_name} is now '{order.status}'!")


class WaiterNotifier(OrderObserver):
    """
    Concrete Observer: Alerts the waitstaff specifically when food becomes completely READY or DELIVERED.
    """
    def update(self, order: Order):
        if order.status == 'READY':
            print(f"\n[WAITER ALERT] 🛎️ Food is ready to be served! Pick up Order #{order.id} ({order.customer_name}).")
        elif order.status == 'DELIVERED':
             print(f"\n[WAITER LOG] Order #{order.id} marked as Delivered.")


class OrderSubject:
    """
    The Publisher/Subject holding the primary state and administrating its dynamic observers.
    """
    def __init__(self):
        self._observers: List[OrderObserver] = []

    def attach(self, observer: OrderObserver):
        """Register an observer to monitor state changes."""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: OrderObserver):
        """Unregister an existing observer."""
        self._observers.remove(observer)

    def notify(self, order: Order):
        """Trigger an update execution in each subscriber concurrently."""
        for observer in self._observers:
            observer.update(order)

    def change_order_status(self, order: Order, new_status: str):
        """
        The core business logic simulation for changing the order status over time and emitting events.
        """
        order.status = new_status
        order.save()
        print(f"\n[SYSTEM MAIN] OrderSubject: Changing underlying Order #{order.id} status strictly to '{new_status}'")
        self.notify(order)
