"""
URL configuration for billing application.
"""
from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Счета
    path('', views.InvoiceListView.as_view(), name='invoice_list'),
    path('create/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('<int:pk>/edit/', views.InvoiceUpdateView.as_view(), name='invoice_update'),
    path('<int:pk>/delete/', views.InvoiceDeleteView.as_view(), name='invoice_delete'),
    path('<int:pk>/pdf/', views.invoice_generate_pdf, name='invoice_pdf'),
    path('<int:pk>/mark-paid/', views.invoice_mark_paid, name='invoice_mark_paid'),
    
    # Платежи
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/create/', views.PaymentCreateView.as_view(), name='payment_create'),
]

