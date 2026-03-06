from django.contrib import admin
from .models import MenuItem, Order

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_type', 'price')
    list_filter = ('item_type',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
