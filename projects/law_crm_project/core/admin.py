"""
Административная панель для core приложения.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Client, ConflictCheck
from auditlog.admin import LogEntryAdmin
from auditlog.models import LogEntry


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Административная панель для пользователей"""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active_lawyer', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active', 'is_active_lawyer']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'naau_certificate_number']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Професійна інформація', {
            'fields': ('role', 'naau_certificate_number', 'hourly_rate', 'is_active_lawyer')
        }),
        ('Контактні дані', {
            'fields': ('phone', 'birth_date', 'photo')
        }),
        ('Банківські реквізити', {
            'fields': ('bank_account',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Додаткова інформація', {
            'fields': ('role', 'email', 'first_name', 'last_name', 'phone')
        }),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Административная панель для клиентов"""
    
    list_display = [
        'id', 'get_name', 'client_type', 'identifier', 
        'phone', 'responsible_lawyer', 'is_active', 'created_at'
    ]
    list_filter = ['client_type', 'is_active', 'created_at', 'responsible_lawyer']
    search_fields = [
        'first_name', 'last_name', 'middle_name', 'company_name', 
        'rnokpp', 'edrpou', 'email', 'phone'
    ]
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Тип клієнта', {
            'fields': ('client_type',)
        }),
        ('Інформація про фізичну особу', {
            'fields': ('first_name', 'last_name', 'middle_name', 'rnokpp', 'passport_data'),
            'classes': ('collapse',),
        }),
        ('Інформація про юридичну особу', {
            'fields': ('company_name', 'edrpou', 'representative_name', 'representative_position'),
            'classes': ('collapse',),
        }),
        ('Контактні дані', {
            'fields': ('email', 'phone', 'phone_additional', 'address')
        }),
        ('Управління', {
            'fields': ('responsible_lawyer', 'is_active', 'notes')
        }),
        ('Системна інформація', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',),
        }),
    )
    
    def get_name(self, obj):
        return obj.full_name
    get_name.short_description = 'Ім\'я / Назва'
    
    def save_model(self, request, obj, form, change):
        if not change:  # При создании
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ConflictCheck)
class ConflictCheckAdmin(admin.ModelAdmin):
    """Административная панель для проверок конфликта интересов"""
    
    list_display = [
        'client', 'opposing_party_name', 'has_conflict', 
        'checked_by', 'checked_at'
    ]
    list_filter = ['has_conflict', 'checked_at']
    search_fields = [
        'client__first_name', 'client__last_name', 'client__company_name',
        'opposing_party_name', 'opposing_party_identifier'
    ]
    readonly_fields = ['checked_at']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.checked_by = request.user
        super().save_model(request, obj, form, change)

