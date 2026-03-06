"""
Singleton Design Pattern Implementation

Pattern Goal: Ensure a class only has one instance, and provide a global point of access to it.

Real-world Problem Solved: 
In a restaurant system, having multiple instances of the system configuration (like tax rate, 
operating hours, or restaurant name) might lead to inconsistent data being used across different 
modules if the configuration is changed at runtime by a manager. A Singleton ensures that any part 
of the application (like a pricing strategy module calculating tax) querying the configuration 
gets the exact same state and memory address.

How it implements the pattern:
The `RestaurantConfigManager` overrides the Python internal `__new__` method. It checks if an instance 
of the class already exists via the `_instance` class attribute. If it does not exist, it creates a new 
instance. If it does exist, it simply returns the existing instance. This guarantees that calling
`RestaurantConfigManager()` will always return the very same object in memory throughout the Django 
application's lifecycle.
"""

class RestaurantConfigManager:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # If no instance exists, create one and initialize the default settings
            cls._instance = super(RestaurantConfigManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize_config()
        return cls._instance
        
    def _initialize_config(self):
        """
        Set up the default configuration for the restaurant upon the first instantiation.
        """
        self.restaurant_name = "The GoF Gourmet"
        self.tax_rate = 0.08  # 8% tax
        self.opening_hour = "08:00"
        self.closing_hour = "23:00"
        self.is_open_today = True

    def update_tax_rate(self, new_rate: float):
        """Update the global tax rate for the restaurant."""
        self.tax_rate = new_rate
        
    def get_tax_rate(self) -> float:
        """Retrieve the global tax rate."""
        return self.tax_rate

    def get_business_hours(self) -> str:
        """Retrieve the formatted business hours."""
        return f"{self.opening_hour} to {self.closing_hour}"
