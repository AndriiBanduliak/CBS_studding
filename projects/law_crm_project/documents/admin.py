"""
Административная панель для documents.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import DocumentCategory, Document, DocumentTemplate


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'documents_count']
    search_fields = ['name', 'description']
    
    def documents_count(self, obj):
        return obj.documents.count()
    documents_count.short_description = 'Кількість документів'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'case', 'document_type', 'document_date',
        'file_size_display', 'is_confidential', 'uploaded_by', 'created_at'
    ]
    list_filter = ['document_type', 'is_confidential', 'document_date', 'created_at']
    search_fields = ['title', 'description', 'registration_number', 
                     'case__case_number', 'case__title']
    readonly_fields = ['file_size', 'uploaded_by', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('case', 'category', 'document_type', 'title', 'description')
        }),
        ('Файл', {
            'fields': ('file', 'file_size')
        }),
        ('Метадані', {
            'fields': ('document_date', 'author_name', 'recipient_name', 'registration_number')
        }),
        ('Доступ', {
            'fields': ('is_confidential',)
        }),
        ('Системна інформація', {
            'fields': ('uploaded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_size_display(self, obj):
        if obj.file_size:
            mb = obj.file_size / (1024 * 1024)
            if mb < 1:
                return f"{obj.file_size / 1024:.1f} KB"
            return f"{mb:.1f} MB"
        return "-"
    file_size_display.short_description = 'Розмір'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'document_type', 'is_active', 'created_by', 'created_at']
    list_filter = ['document_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

