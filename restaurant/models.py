from django.db import models

class MenuItem(models.Model):
    """
    Core Model representing an item available in the restaurant.
    We keep it simple to allow Patterns (Factory, Decorator) to build upon it.
    """
    ITEM_TYPES = [
        ('VEG', 'Vegetarian'),
        ('NON_VEG', 'Non-Vegetarian'),
        ('VEGAN', 'Vegan'),
    ]
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class RestaurantTable(models.Model):
    """
    Model representing a physical table in the restaurant.
    """
    table_number = models.IntegerField(unique=True)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"Table {self.table_number}"

class Order(models.Model):
    """
    Core Model representing a customer's order.
    The status changes later will trigger our Observer pattern.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready'),
        ('DELIVERED', 'Delivered'),
        ('COMPLETED', 'Completed'),
    ]
    customer_name = models.CharField(max_length=100)
    table = models.ForeignKey(RestaurantTable, on_delete=models.CASCADE, null=True, blank=True)
    items = models.ManyToManyField(MenuItem)
    item_description = models.TextField(blank=True, help_text="Decorated order description")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"
