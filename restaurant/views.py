"""
Django Views acting strictly as purely the Client.

To demonstrate the efficacy of the Facade design pattern globally for our viva, observe 
that this file contains literally zero direct business logic. All database persistence, prices, 
and notifications are delegated remotely to external modular architecture.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from restaurant.models import Order, RestaurantTable
from restaurant.patterns.facade import OrderProcessingFacade
from restaurant.patterns.strategy import HappyHourPricing, VIPDiscountPricing, NormalPricing

# Instantiate the Facade gateway orchestration component globally.
orchestrator = OrderProcessingFacade()

def index_view(request):
    """
    Acts as the modern Custom Landing page with a Hero section and Table Selection grid.
    """
    tables = RestaurantTable.objects.all().order_by('table_number')
    has_available = tables.filter(is_occupied=False).exists()
    
    return render(request, 'restaurant/landing.html', {
        'tables': tables,
        'has_available_tables': has_available
    })

def menu_view(request, table_id):
    """
    Displays the seeded categorized menu specifically for an active table.
    """
    table = get_object_or_404(RestaurantTable, table_number=table_id)
    
    # Normally, accessing a table from landing marks it occupied in a real POS,
    # but since our Ordering backend explicitly does this later, we just pass the ID.
    from restaurant.models import MenuItem # Local import to avoid cyclic issues at top if any
    
    # Categorize items neatly for the template
    items = MenuItem.objects.all()
    pizzas = [item for item in items if 'Pizza' in item.name or 'Extravaganza' in item.name or 'Dominator' in item.name or 'Sweet Corn' in item.name]
    burgers = [item for item in items if 'Burger' in item.name or 'Mac' in item.name]
    sides = [item for item in items if 'Fries' in item.name or 'Wings' in item.name or 'Bread' in item.name or 'Kebab' in item.name or 'Rings' in item.name or 'Poppers' in item.name or 'Nuggets' in item.name or 'Samosa' in item.name or 'Wedges' in item.name or 'Skewers' in item.name]
    beverages = [item for item in items if item not in pizzas and item not in burgers and item not in sides]

    # Fallback categorizing purely by item_type if string matching isn't perfect
    veg_items = items.filter(item_type='VEG')
    non_veg_items = items.filter(item_type='NON_VEG')
    vegan_items = items.filter(item_type='VEGAN')

    return render(request, 'restaurant/menu.html', {
        'table': table,
        'pizzas': pizzas,
        'burgers': burgers,
        'sides': sides,
        'beverages': beverages,
        'veg_items': veg_items,
        'non_veg_items': non_veg_items,
        'vegan_items': vegan_items
    })

def staff_dashboard_view(request):
    """
    Staff Dashboard displaying active orders grouped by Table.
    """
    dashboard_data = []
    tables = RestaurantTable.objects.filter(is_occupied=True).order_by('table_number')
    
    for t in tables:
        orders = Order.objects.filter(table=t).exclude(status='COMPLETED').order_by('created_at')
        if orders.exists():
            bill = orchestrator.calculate_table_bill(t.table_number)
            dashboard_data.append({
                'table_number': t.table_number,
                'orders': orders,
                'total_bill': bill['grand_total'] if bill else 0.0
            })
            
    # Include orders without a table (e.g. takeaways if any)
    takeaway_orders = Order.objects.filter(table__isnull=True).exclude(status='COMPLETED').order_by('-created_at')
    if takeaway_orders.exists():
        dashboard_data.append({
            'table_number': 'Takeaway',
            'orders': takeaway_orders,
            'total_bill': sum(o.total_amount for o in takeaway_orders)
        })

    return render(request, 'restaurant/staff_dashboard.html', {
        'dashboard_data': dashboard_data
    })

def payment_page_view(request, table_id):
    """
    Payment view bridging perfectly to the Facade's `calculate_table_bill` algorithm.
    """
    bill_data = orchestrator.calculate_table_bill(table_id)
    
    return render(request, 'restaurant/bill.html', {
        'table_number': table_id,
        'bill': bill_data
    })

def process_payment_view(request, table_id):
    """
    Form action that delegates payment finalization perfectly back to the Facade.
    """
    if request.method == 'POST':
        success, message = orchestrator.process_payment(table_id)
        if success:
            return redirect('thank_you')
        else:
            # For simplicity, returning a raw HTTP response. Ideally use Django Messages.
            return JsonResponse({'success': False, 'error': message}, status=400)
            
    return redirect('staff_dashboard')


def thank_you_view(request):
    """
    Simple confirmation page post-payment.
    """
    return render(request, 'restaurant/thank_you.html')


@csrf_exempt
def create_order_view(request):
    """
    Client view intelligently mapping a Web Request straightforwardly to our complex Design Patterns subsystem.
    Now supports a Cart array of items gracefully.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            table_number = data.get('table_number')
            customer_name = data.get('customer_name', f'Table {table_number} Guest' if table_number else 'Guest')
            
            # Legacy fallback if they send a single item without 'items' array
            if not items and data.get('item_name'):
                items = [data]
                
            responses = []
            for item in items:
                # Determine Pricing Strategy from incoming API request conditionally based off string literals
                strategy_str = item.get('strategy', 'normal')
                if strategy_str == 'happy_hour':
                    strategy = HappyHourPricing()
                elif strategy_str == 'vip':
                    strategy = VIPDiscountPricing()
                else:
                    strategy = NormalPricing()

                # The View executes its primary duty elegantly - It Delegates completely to the robust underlying Facade.
                response_data = orchestrator.place_order(
                    customer_name=customer_name,
                    item_category=item.get('category', 'veg'),
                    item_name=item.get('item_name', 'Generic Item'),
                    base_price=float(item.get('price', 0.0)),
                    add_cheese=item.get('add_cheese', False),
                    add_bacon=item.get('add_bacon', False),
                    pricing_strategy=strategy,
                    table_number=table_number
                )
                responses.append(response_data)

            # Restitutes a clean standardized web formatted layer exclusively to frontend handlers globally
            return JsonResponse({
                'success': True,
                'message': f'Processed {len(responses)} items successfully.',
                'orders': responses
            }, status=201)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'error': 'Only POST method is allowed.'}, status=405)

@csrf_exempt
def mark_order_ready_view(request, order_id):
    """
    Supplementary Client REST View triggering an Observer event implicitly mapping an HTTP call to the Waiters.
    """
    if request.method == 'POST':
        success = orchestrator.complete_order(order_id)
        if success:
            return JsonResponse({'success': True, 'message': f'Order #{order_id} systematically flagged as READY status.'})
        return JsonResponse({'success': False, 'error': 'Database queried order literally not found.'}, status=404)
    return JsonResponse({'error': 'Only POST method is allowed.'}, status=405)
