"""
Factory Method Design Pattern Implementation

Pattern Goal: Define an interface for creating an object, but let subclasses decide which class to instantiate.

Real-world Problem Solved: 
When a new menu item is added to the system, it requires specific default values or business logic 
(e.g., all Vegan items need to be strictly categorized, and their descriptions might need a 
mandatory allergy/ingredient warning). Hardcoding `MenuItem.objects.create(name=..., item_type='VEGAN')` 
in views pollutes the business logic. The Factory Method encapsulates this instantiation logic. 
If we need to change how a "Vegan" item is created (e.g., adding an extra default text), we only update 
the factory, preventing tight coupling throughout the views.

How it implements the pattern:
`MenuItemFactory` is the abstract creator providing an interface `create_item`. We have specific concrete 
factories (`VegMenuItemFactory`, `NonVegMenuItemFactory`, `VeganMenuItemFactory`) that handle the actual 
instantiation of the Django ORM `MenuItem` instances. It decides how the database object is built and returned, 
ensuring the type-specific constraints (like `item_type`) are enforced automatically without the client (e.g., views)
knowing the database-level details.
"""

from restaurant.models import MenuItem

class MenuItemFactory:
    """
    Abstract creator. Defines the factory method interface.
    """
    @classmethod
    def create_item(cls, name: str, price: float, description: str = "") -> MenuItem:
        """
        Factory method to be implemented by robust concrete factories.
        """
        raise NotImplementedError("Subclasses must implement create_item")


class VegMenuItemFactory(MenuItemFactory):
    """
    Concrete creator for Vegetarian Menu Items.
    """
    @classmethod
    def create_item(cls, name: str, price: float, description: str = "") -> MenuItem:
        # Encapsulates the logic of what makes a veg item (setting item_type='VEG')
        return MenuItem.objects.create(
            name=name,
            price=price,
            item_type='VEG',
            description=f"[VEG] {description}"
        )


class NonVegMenuItemFactory(MenuItemFactory):
    """
    Concrete creator for Non-Vegetarian Menu Items.
    """
    @classmethod
    def create_item(cls, name: str, price: float, description: str = "") -> MenuItem:
        return MenuItem.objects.create(
            name=name,
            price=price,
            item_type='NON_VEG',
            description=f"[NON-VEG] {description}"
        )


class VeganMenuItemFactory(MenuItemFactory):
    """
    Concrete creator for Vegan Menu Items.
    """
    @classmethod
    def create_item(cls, name: str, price: float, description: str = "") -> MenuItem:
        return MenuItem.objects.create(
            name=name,
            price=price,
            item_type='VEGAN',
            description=f"[VEGAN - NO DAIRY/MEAT] {description}"
        )


class SimpleMenuFactory:
    """
    A Parameterized Simple Factory. 
    Often used in Python alongside the GoF Factory Method to allow a router-like creation approach.
    """
    _factories = {
        'veg': VegMenuItemFactory,
        'non_veg': NonVegMenuItemFactory,
        'vegan': VeganMenuItemFactory,
    }

    @classmethod
    def get_item(cls, item_category: str, name: str, price: float, description: str = "") -> MenuItem:
        factory_cls = cls._factories.get(item_category.lower())
        if not factory_cls:
            raise ValueError(f"Unknown menu item category: {item_category}")
        return factory_cls.create_item(name, price, description)
