from django.contrib import admin
from .models import MenuItem, Order, RestaurantTable
from .patterns.facade import OrderProcessingFacade

orchestrator = OrderProcessingFacade()

@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'is_occupied', 'get_active_orders_count', 'get_current_bill')
    list_filter = ('is_occupied',)
    list_editable = ('is_occupied',)
    search_fields = ('table_number',)
    ordering = ('table_number',)
    actions = ['mark_as_vacant', 'mark_as_occupied', 'clear_and_vacate_tables']

    @admin.display(description='Active Orders')
    def get_active_orders_count(self, obj):
        count = Order.objects.filter(table=obj).exclude(status='COMPLETED').count()
        return f"{count} orders" if count else "0 (No orders)"

    @admin.display(description='Live Table Bill (₹)')
    def get_current_bill(self, obj):
        if not obj.is_occupied:
            return "₹0.00 (Vacant)"
        bill = orchestrator.calculate_table_bill(obj.table_number)
        return f"₹{bill['grand_total']:.2f}" if bill else "₹0.00"

    @admin.action(description='Mark selected tables as Vacant (Available)')
    def mark_as_vacant(self, request, queryset):
        count = queryset.update(is_occupied=False)
        self.message_user(request, f"{count} table(s) successfully marked as VACANT.")

    @admin.action(description='Mark selected tables as Occupied')
    def mark_as_occupied(self, request, queryset):
        count = queryset.update(is_occupied=True)
        self.message_user(request, f"{count} table(s) successfully marked as OCCUPIED.")

    @admin.action(description='Complete orders and Vacate selected tables')
    def clear_and_vacate_tables(self, request, queryset):
        for table in queryset:
            Order.objects.filter(table=table).exclude(status='COMPLETED').update(status='COMPLETED', is_paid=True)
            table.is_occupied = False
            table.save()
        self.message_user(request, f"Active orders completed and {queryset.count()} table(s) marked as VACANT.")


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_type', 'price')
    list_filter = ('item_type',)
    search_fields = ('name', 'description')
    ordering = ('price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'table', 'status', 'total_amount', 'is_paid', 'created_at')
    list_filter = ('status', 'is_paid', 'created_at')
    search_fields = ('customer_name', 'id')
    ordering = ('-created_at',)
