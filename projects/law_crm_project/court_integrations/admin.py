"""
Административная панель для court_integrations.
"""
from django.contrib import admin
from .models import EGRSRSync, CourtDecision


@admin.register(EGRSRSync)
class EGRSRSyncAdmin(admin.ModelAdmin):
    list_display = [
        'case', 'sync_date', 'status', 'records_found', 'new_decisions'
    ]
    list_filter = ['status', 'sync_date']
    search_fields = ['case__case_number', 'case__title']
    readonly_fields = ['sync_date', 'response_data']


@admin.register(CourtDecision)
class CourtDecisionAdmin(admin.ModelAdmin):
    list_display = [
        'case', 'decision_type', 'decision_date', 'judge_name', 'is_new', 'imported_at'
    ]
    list_filter = ['decision_type', 'is_new', 'decision_date']
    search_fields = [
        'case__case_number', 'decision_id', 'judge_name', 'summary'
    ]
    readonly_fields = ['decision_id', 'imported_at']
    date_hierarchy = 'decision_date'

