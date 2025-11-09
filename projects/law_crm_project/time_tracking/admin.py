"""
Административная панель для time_tracking.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import WorkType, TimeEntry, Timer


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'default_rate', 'is_billable', 'is_active']
    list_filter = ['is_billable', 'is_active']
    search_fields = ['name', 'description']


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'case', 'work_type', 'date', 'duration_hours', 
        'total_amount', 'is_billable', 'is_billed'
    ]
    list_filter = ['is_billable', 'is_billed', 'work_type', 'date', 'user']
    search_fields = [
        'user__first_name', 'user__last_name', 
        'case__case_number', 'case__title', 'description'
    ]
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('user', 'case', 'work_type', 'date')
        }),
        ('Час роботи', {
            'fields': ('start_time', 'end_time', 'duration_hours')
        }),
        ('Опис', {
            'fields': ('description', 'notes')
        }),
        ('Фінанси', {
            'fields': ('hourly_rate', 'total_amount', 'is_billable', 'is_billed', 'invoice')
        }),
        ('Системна інформація', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'case', 'work_type', 'invoice')


@admin.register(Timer)
class TimerAdmin(admin.ModelAdmin):
    list_display = ['user', 'case', 'work_type', 'start_time', 'elapsed_time_display', 'is_paused']
    list_filter = ['is_paused', 'start_time']
    search_fields = ['user__first_name', 'user__last_name', 'case__case_number']
    readonly_fields = ['start_time', 'elapsed_time_display']
    
    def elapsed_time_display(self, obj):
        elapsed = obj.get_elapsed_time()
        hours = int(elapsed.total_seconds() // 3600)
        minutes = int((elapsed.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"
    elapsed_time_display.short_description = 'Минуло часу'

