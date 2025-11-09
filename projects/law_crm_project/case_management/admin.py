"""
Административная панель для case_management.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Court, Case, LawyerOrder, CaseEvent, CaseNote


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ['name', 'court_type', 'address', 'phone']
    list_filter = ['court_type']
    search_fields = ['name', 'address']


class LawyerOrderInline(admin.TabularInline):
    model = LawyerOrder
    extra = 1
    fields = ['lawyer', 'order_series', 'order_number', 'issue_date', 'is_active']


class CaseEventInline(admin.TabularInline):
    model = CaseEvent
    extra = 0
    fields = ['event_type', 'title', 'event_date', 'is_completed']
    readonly_fields = ['created_at']


class CaseNoteInline(admin.StackedInline):
    model = CaseNote
    extra = 0
    fields = ['author', 'content', 'is_important']
    verbose_name = 'Нотатка'
    verbose_name_plural = 'Нотатки'


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = [
        'case_number', 'title', 'client', 'status_badge', 
        'proceeding_type', 'responsible_lawyer', 'next_hearing_date', 'is_priority'
    ]
    list_filter = ['status', 'proceeding_type', 'is_priority', 'court', 'created_at']
    search_fields = ['case_number', 'title', 'description', 'client__first_name', 
                     'client__last_name', 'client__company_name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'last_egrsr_sync']
    filter_horizontal = ['lawyers', 'assistants']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('case_number', 'title', 'description', 'proceeding_type', 'status')
        }),
        ('Учасники', {
            'fields': ('client', 'opposing_party', 'opposing_party_lawyer')
        }),
        ('Суд', {
            'fields': ('court', 'judge')
        }),
        ('Команда адвокатів', {
            'fields': ('responsible_lawyer', 'lawyers', 'assistants')
        }),
        ('Важливі дати', {
            'fields': ('registration_date', 'first_hearing_date', 'next_hearing_date', 
                      'deadline_date', 'closed_date')
        }),
        ('Інтеграція з ЄДРСР', {
            'fields': ('egrsr_id', 'last_egrsr_sync'),
            'classes': ('collapse',)
        }),
        ('Фінанси', {
            'fields': ('estimated_value', 'contract_amount')
        }),
        ('Додатково', {
            'fields': ('notes', 'is_priority')
        }),
        ('Системна інформація', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [LawyerOrderInline, CaseEventInline, CaseNoteInline]
    
    def status_badge(self, obj):
        colors = {
            'new': '#6c757d',
            'consultation': '#17a2b8',
            'contract_preparation': '#ffc107',
            'in_progress': '#007bff',
            'suspended': '#6c757d',
            'closed_won': '#28a745',
            'closed_lost': '#dc3545',
            'closed_settled': '#20c997',
            'archived': '#6c757d',
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


@admin.register(LawyerOrder)
class LawyerOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number_full', 'lawyer', 'case', 'issue_date', 'is_active']
    list_filter = ['is_active', 'issue_date', 'lawyer']
    search_fields = ['order_series', 'order_number', 'lawyer__first_name', 
                     'lawyer__last_name', 'case__case_number']
    date_hierarchy = 'issue_date'
    
    def order_number_full(self, obj):
        return f"{obj.order_series}-{obj.order_number}"
    order_number_full.short_description = 'Номер ордера'


@admin.register(CaseEvent)
class CaseEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'case', 'event_type', 'event_date', 'is_completed', 'reminder_sent']
    list_filter = ['event_type', 'is_completed', 'reminder_sent', 'event_date']
    search_fields = ['title', 'description', 'case__case_number']
    date_hierarchy = 'event_date'
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CaseNote)
class CaseNoteAdmin(admin.ModelAdmin):
    list_display = ['case', 'author', 'content_preview', 'is_important', 'created_at']
    list_filter = ['is_important', 'created_at']
    search_fields = ['content', 'case__case_number']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Зміст'

