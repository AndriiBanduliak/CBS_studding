from django_filters import rest_framework as filters
from .models import Transaction


class TransactionFilter(filters.FilterSet):
    """
    Фильтр для транзакций с поддержкой фильтрации по категории и диапазону дат.
    """
    category_id = filters.NumberFilter(field_name='category__id')
    date_from = filters.DateTimeFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateTimeFilter(field_name='date', lookup_expr='lte')
    
    class Meta:
        model = Transaction
        fields = ['category_id', 'date_from', 'date_to']

