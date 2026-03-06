"""
Decorator Design Pattern Implementation

Pattern Goal: Attach additional responsibilities to an object dynamically. Decorators provide
a flexible alternative to subclassing for extending functionality.

Real-world Problem Solved:
In a restaurant catering scenario, a single menu item (like a 'Burger') can have dozens of customizations 
(Extra Cheese, Add Bacon, No Onion, Gluten-Free Bun, Extra Spicy). Trying to create unique subclasses in your models 
for every combination (e.g., `Class BurgerWithCheese`, `Class BurgerWithCheeseAndBacon`) leads to a "class explosion".
We need to calculate the price and updated description of an item on the fly through an add-on system without altering
the original core object.

How it implements the pattern:
Instead of relying on rigid Django ORM subclasses for every food variation, we use an in-memory 
wrapper architecture. We define a base interface `ItemComponent` and implement the base items representing the core ORM object.
The `ItemDecorator` class implements the same interface and holds a tight reference to an `ItemComponent`. The concrete
decorators (`ExtraCheeseDecorator`, `AddBaconDecorator`) literally "wrap" the core item, adding their own cost to its price 
and recursively appending their specific features to its description.
"""

from abc import ABC, abstractmethod
from restaurant.models import MenuItem

class ItemComponent(ABC):
    """
    The base Component interface defining operations that can be altered by decorators.
    """
    @abstractmethod
    def get_price(self) -> float:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass


class MenuItemComponent(ItemComponent):
    """
    Concrete Component representing a base menu item pulled from our database factory.
    It acts as the pristine core object being wrapped in decorators.
    """
    def __init__(self, menu_item: MenuItem):
        self.menu_item = menu_item

    def get_price(self) -> float:
        return float(self.menu_item.price)

    def get_description(self) -> str:
        return self.menu_item.name


class ItemDecorator(ItemComponent):
    """
    The base Decorator class follows the identical interface as the other components.
    The primary purpose of this class is to define the wrapping interface (the `_wrapped_item` reference) 
    for all concrete decorators to build upon.
    """
    def __init__(self, wrapped_item: ItemComponent):
        self._wrapped_item = wrapped_item

    def get_price(self) -> float:
        return self._wrapped_item.get_price()

    def get_description(self) -> str:
        return self._wrapped_item.get_description()


class ExtraCheeseDecorator(ItemDecorator):
    """
    Concrete Decorator adding cheese to an item.
    """
    def get_price(self) -> float:
        # Intercepts the function to add $1.50 for extra cheese over the wrapped base price
        return self._wrapped_item.get_price() + 1.50

    def get_description(self) -> str:
        # Appends the extra feature to the wrapped description
        return self._wrapped_item.get_description() + " + Extra Cheese"


class AddBaconDecorator(ItemDecorator):
    """
    Concrete Decorator adding extra bacon to an item.
    """
    def get_price(self) -> float:
        # Intercepts the function to add $2.50 for bacon
        return self._wrapped_item.get_price() + 2.50

    def get_description(self) -> str:
        return self._wrapped_item.get_description() + " + Bacon"
