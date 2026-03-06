from django.urls import path
from . import views

urlpatterns = [
    # UI Routes
    path('', views.index_view, name='index'),
    path('menu/<int:table_id>/', views.menu_view, name='menu_page'),
    path('staff-dashboard/', views.staff_dashboard_view, name='staff_dashboard'),
    path('bill/<int:table_id>/', views.payment_page_view, name='payment_page'),
    path('payment/<int:table_id>/process/', views.process_payment_view, name='process_payment'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
    
    # API Routes calling the Facade
    path('api/order', views.create_order_view, name='api_create_order'),
    path('api/order/<int:order_id>/ready', views.mark_order_ready_view, name='api_order_ready'),
]
