"""
Django Views acting strictly as purely the Client.

To demonstrate the efficacy of the Facade design pattern globally for our viva, observe 
that this file contains literally zero direct business logic. All database persistence, prices, 
and notifications are delegated remotely to external modular architecture.
"""

import io
import json
import queue
import threading
import zipfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse, StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from restaurant.models import Order, RestaurantTable
from restaurant.patterns.facade import OrderProcessingFacade
from restaurant.patterns.strategy import HappyHourPricing, VIPDiscountPricing, NormalPricing
from restaurant.reporting import TEST_SUITES, generate_all_reports

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
    items = list(MenuItem.objects.all().order_by('price'))
    pizzas = [item for item in items if 'Pizza' in item.name or 'Extravaganza' in item.name or 'Dominator' in item.name or 'Sweet Corn' in item.name]
    burgers = [item for item in items if 'Burger' in item.name or 'Mac' in item.name]
    sides = [item for item in items if 'Fries' in item.name or 'Wings' in item.name or 'Bread' in item.name or 'Kebab' in item.name or 'Rings' in item.name or 'Poppers' in item.name or 'Nuggets' in item.name or 'Samosa' in item.name or 'Wedges' in item.name or 'Skewers' in item.name]
    beverages = [item for item in items if item not in pizzas and item not in burgers and item not in sides]

    # Fallback categorizing purely by item_type if string matching isn't perfect
    veg_items = [i for i in items if i.item_type == 'VEG']
    non_veg_items = [i for i in items if i.item_type == 'NON_VEG']
    vegan_items = [i for i in items if i.item_type == 'VEGAN']

    return render(request, 'restaurant/menu.html', {
        'table': table,
        'pizzas': pizzas,
        'burgers': burgers,
        'sides': sides,
        'beverages': beverages,
        'veg_items': veg_items,
        'non_veg_items': non_veg_items,
        'vegan_items': vegan_items,
        'all_items': items,
        'total_items_count': len(items)
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


def table_admin_view(request):
    """
    Dedicated Table Vacancy & Floor Management Admin Panel.
    Allows managers to inspect live occupancy, toggle table vacancy,
    clear table orders, and execute bulk vacancy operations.
    """
    tables = RestaurantTable.objects.all().order_by('table_number')
    
    table_details = []
    total_active_orders = 0
    total_active_revenue = 0.0
    
    for t in tables:
        active_orders = Order.objects.filter(table=t).exclude(status='COMPLETED').order_by('-created_at')
        orders_count = active_orders.count()
        total_active_orders += orders_count
        
        bill_data = None
        bill_amount = 0.0
        if t.is_occupied:
            bill_data = orchestrator.calculate_table_bill(t.table_number)
            if bill_data:
                bill_amount = float(bill_data.get('grand_total', 0.0))
                total_active_revenue += bill_amount

        first_order = active_orders.first()
        table_details.append({
            'table': t,
            'table_number': t.table_number,
            'is_occupied': t.is_occupied,
            'orders_count': orders_count,
            'orders': active_orders,
            'bill_amount': bill_amount,
            'customer_name': first_order.customer_name if first_order else (f"Table {t.table_number} Guest" if t.is_occupied else None),
            'latest_order_time': first_order.created_at.strftime("%I:%M %p") if first_order else None
        })

    total_count = len(table_details)
    occupied_count = sum(1 for item in table_details if item['is_occupied'])
    vacant_count = total_count - occupied_count
    occupancy_percentage = round((occupied_count / total_count * 100), 1) if total_count > 0 else 0.0

    return render(request, 'restaurant/table_admin.html', {
        'table_details': table_details,
        'total_tables': total_count,
        'occupied_tables': occupied_count,
        'vacant_tables': vacant_count,
        'occupancy_percentage': occupancy_percentage,
        'total_active_orders': total_active_orders,
        'total_active_revenue': total_active_revenue,
    })


@csrf_exempt
def api_toggle_table_vacancy(request, table_id):
    """
    API endpoint to toggle or explicitly set table vacancy status.
    """
    table = get_object_or_404(RestaurantTable, table_number=table_id)
    
    if request.method == 'POST':
        try:
            if request.body:
                try:
                    data = json.loads(request.body)
                    if 'is_occupied' in data:
                        table.is_occupied = bool(data['is_occupied'])
                    else:
                        table.is_occupied = not table.is_occupied
                except Exception:
                    table.is_occupied = not table.is_occupied
            else:
                table.is_occupied = not table.is_occupied
                
            table.save()
            status_text = "OCCUPIED" if table.is_occupied else "VACANT"
            return JsonResponse({
                'success': True,
                'table_number': table.table_number,
                'is_occupied': table.is_occupied,
                'status_text': status_text,
                'message': f"Table {table.table_number} is now {status_text}."
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'error': 'POST method required.'}, status=405)


@csrf_exempt
def api_clear_table_orders(request, table_id):
    """
    Clears all active orders for a table, marks them completed/paid, and sets table to Vacant.
    """
    if request.method == 'POST':
        table = get_object_or_404(RestaurantTable, table_number=table_id)
        orders = Order.objects.filter(table=table).exclude(status='COMPLETED')
        count = orders.count()
        orders.update(status='COMPLETED', is_paid=True)
        table.is_occupied = False
        table.save()
        
        return JsonResponse({
            'success': True,
            'table_number': table.table_number,
            'is_occupied': False,
            'cleared_orders_count': count,
            'message': f"Table {table.table_number} cleared ({count} order(s)) and marked VACANT."
        })

    return JsonResponse({'error': 'POST method required.'}, status=405)


@csrf_exempt
def api_bulk_table_action(request):
    """
    Bulk operation to free all tables or occupy all tables.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            action = data.get('action', request.POST.get('action', 'free_all'))
            
            if action == 'free_all':
                RestaurantTable.objects.all().update(is_occupied=False)
                if data.get('complete_orders', False):
                    Order.objects.filter(table__isnull=False).exclude(status='COMPLETED').update(status='COMPLETED', is_paid=True)
                return JsonResponse({'success': True, 'message': 'All tables marked as VACANT.'})
            elif action == 'occupy_all':
                RestaurantTable.objects.all().update(is_occupied=True)
                return JsonResponse({'success': True, 'message': 'All tables marked as OCCUPIED.'})
            else:
                return JsonResponse({'success': False, 'error': 'Unknown bulk action.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'error': 'POST method required.'}, status=405)


def test_reports_view(request):
    reports_dir = Path(settings.BASE_DIR) / 'test_reports'
    topics_guide_file = reports_dir / 'testing_topics_guide.xlsx'
    topics_guide_available = topics_guide_file.is_file()

    suites = []
    any_available = False
    for slug, suite in TEST_SUITES.items():
        report_file = reports_dir / f'{slug}.xlsx'
        is_avail = report_file.is_file()
        if is_avail:
            any_available = True
        suites.append({
            'slug': slug,
            'title': suite['title'],
            'description': suite['description'],
            'available': is_avail,
            'filename': f'{slug}.xlsx',
            'filesize': f'{report_file.stat().st_size / 1024:.1f} KB' if is_avail else None,
            'updated_at': datetime.fromtimestamp(report_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S') if is_avail else None,
        })

    return render(request, 'restaurant/test_reports.html', {
        'suites': suites,
        'topics_guide_available': topics_guide_available,
        'all_reports_available': any_available or topics_guide_available,
        'total_suites': len(TEST_SUITES),
    })


def download_test_report_view(request, suite):
    reports_dir = Path(settings.BASE_DIR) / 'test_reports'

    if suite in ('topics-guide', 'testing_topics_guide', 'testing-topics-guide', 'guide'):
        report_path = reports_dir / 'testing_topics_guide.xlsx'
        filename = 'SmartResto_Testing_Topics_and_Methodology_Guide.xlsx'
    elif suite in TEST_SUITES:
        report_path = reports_dir / f'{suite}.xlsx'
        filename = f'{suite}_test_report.xlsx'
    else:
        raise Http404('Test report not found.')

    if not report_path.is_file():
        raise Http404('This report is not available yet. Please click Start Testing Process first.')

    return FileResponse(
        report_path.open('rb'),
        as_attachment=True,
        filename=filename,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


def download_all_reports_view(request):
    reports_dir = Path(settings.BASE_DIR) / 'test_reports'
    xlsx_files = list(reports_dir.glob('*.xlsx')) if reports_dir.is_dir() else []

    if not xlsx_files:
        raise Http404('No test reports have been generated yet. Please run the automated testing process first.')

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in xlsx_files:
            zip_file.write(file_path, arcname=file_path.name)

    zip_buffer.seek(0)
    return FileResponse(
        zip_buffer,
        as_attachment=True,
        filename='SmartResto_Automated_Test_Reports.zip',
        content_type='application/zip',
    )


@csrf_exempt
def run_tests_api_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed. Use POST.'}, status=405)

    logs = []

    def log_collector(event):
        msg = event.get('message')
        if msg:
            logs.append({
                'type': event.get('type', 'log'),
                'message': msg,
                'progress': event.get('progress'),
                'slug': event.get('slug'),
                'timestamp': datetime.now().strftime('%H:%M:%S'),
            })

    try:
        summary = generate_all_reports(progress_callback=log_collector)
        return JsonResponse({
            'success': summary['success'],
            'summary': summary,
            'logs': logs,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'logs': logs,
        }, status=500)


def run_tests_stream_view(request):
    """
    Server-Sent Events (SSE) streaming endpoint.
    Emits real-time progress and logs as test suites execute.
    """
    def event_stream():
        event_queue = queue.Queue()

        def push_event(event):
            event_queue.put(event)

        runner_thread = threading.Thread(
            target=lambda: (
                generate_all_reports(progress_callback=push_event),
                event_queue.put({'type': '__DONE__'})
            )[0]
        )
        runner_thread.daemon = True
        runner_thread.start()

        while True:
            try:
                event = event_queue.get(timeout=10)
                if event.get('type') == '__DONE__':
                    break
                payload = json.dumps(event)
                yield f"data: {payload}\n\n"
            except queue.Empty:
                if not runner_thread.is_alive():
                    break
                yield f": keep-alive\n\n"

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def testing_guide_view(request):
    """
    Renders the Comprehensive Academic Testing Guide and Topic Explanations.
    """
    reports_dir = Path(settings.BASE_DIR) / 'test_reports'
    guide_available = (reports_dir / 'testing_topics_guide.xlsx').is_file()
    return render(request, 'restaurant/testing_guide.html', {
        'guide_available': guide_available,
    })


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

            if not items:
                return JsonResponse({'success': False, 'error': 'No order items specified.'}, status=400)

            responses = []
            for idx, item in enumerate(items):
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
                    table_number=table_number,
                    allow_occupied_table=(idx > 0)
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
