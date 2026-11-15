from django.urls import path
from . import views

urlpatterns = [
    # UI Routes
    path('', views.index_view, name='index'),
    path('menu/<int:table_id>/', views.menu_view, name='menu_page'),
    path('staff-dashboard/', views.staff_dashboard_view, name='staff_dashboard'),
    path('testing/', views.test_reports_view, name='test_reports'),
    path('testing/reports/<slug:suite>/', views.download_test_report_view, name='download_test_report'),
    path('testing/download-all/', views.download_all_reports_view, name='download_all_reports'),
    path('testing/run/', views.run_tests_api_view, name='run_tests_api'),
    path('testing/run-stream/', views.run_tests_stream_view, name='run_tests_stream'),
    path('testing/guide/', views.testing_guide_view, name='testing_guide'),
    path('bill/<int:table_id>/', views.payment_page_view, name='payment_page'),
    path('payment/<int:table_id>/process/', views.process_payment_view, name='process_payment'),
    path('thank-you/', views.thank_you_view, name='thank_you'),

    # Table Vacancy Admin Panel & APIs
    path('table-admin/', views.table_admin_view, name='table_admin'),
    path('api/table/<int:table_id>/toggle-vacancy', views.api_toggle_table_vacancy, name='api_toggle_table_vacancy'),
    path('api/table/<int:table_id>/clear-orders', views.api_clear_table_orders, name='api_clear_table_orders'),
    path('api/table/bulk-action', views.api_bulk_table_action, name='api_bulk_table_action'),

    # API Routes calling the Facade
    path('api/order', views.create_order_view, name='api_create_order'),
    path('api/order/<int:order_id>/ready', views.mark_order_ready_view, name='api_order_ready'),
]
