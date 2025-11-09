"""
Административная панель для billing.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, InvoiceItem, Payment


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['description', 'quantity', 'unit_price', 'total', 'order']
    readonly_fields = ['total']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ['amount', 'payment_date', 'payment_method', 'reference_number']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'case', 'client', 'status_badge',
        'issue_date', 'total', 'due_date', 'paid_date'
    ]
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = [
        'invoice_number', 'case__case_number', 'client__first_name',
        'client__last_name', 'client__company_name'
    ]
    readonly_fields = ['tax_amount', 'total', 'created_at', 'updated_at']
    date_hierarchy = 'issue_date'
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('invoice_number', 'case', 'client', 'status')
        }),
        ('Дати', {
            'fields': ('issue_date', 'due_date', 'paid_date')
        }),
        ('Фінанси', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'total')
        }),
        ('Опис', {
            'fields': ('description', 'notes')
        }),
        ('Реквізити адвоката', {
            'fields': ('lawyer_name', 'lawyer_certificate', 'lawyer_bank_account')
        }),
        ('Системна інформація', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [InvoiceItemInline, PaymentInline]
    
    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'sent': '#17a2b8',
            'paid': '#28a745',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Статус'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'quantity', 'unit_price', 'total']
    list_filter = ['invoice__status']
    search_fields = ['description', 'invoice__invoice_number']
    readonly_fields = ['total']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'invoice', 'amount', 'payment_date', 'payment_method',
        'reference_number', 'received_by'
    ]
    list_filter = ['payment_method', 'payment_date']
    search_fields = [
        'invoice__invoice_number', 'reference_number',
        'invoice__client__first_name', 'invoice__client__last_name'
    ]
    date_hierarchy = 'payment_date'

