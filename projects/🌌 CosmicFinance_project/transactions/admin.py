from django.contrib import admin
from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Административная панель для управления категориями.
    """
    list_display = ['name', 'type', 'user']
    list_filter = ['type', 'user']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Административная панель для управления транзакциями.
    """
    list_display = ['category', 'amount', 'user', 'date', 'created_at']
    list_filter = ['category__type', 'date', 'user']
    search_fields = ['description', 'category__name']
    date_hierarchy = 'date'

