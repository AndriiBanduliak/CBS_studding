"""
Service Layer для бизнес-логики транзакций.
Здесь реализованы сложные операции с использованием Django ORM.
"""

from django.db.models import Sum, Q, Value, DecimalField
from django.db.models.functions import TruncMonth, Coalesce
from django.utils import timezone
from datetime import timedelta
from .models import Transaction, Category


class TransactionAnalyticsService:
    """
    Сервис для аналитических операций с транзакциями.
    """
    
    @staticmethod
    def get_monthly_summary(user, months=12):
        """
        Получить сводку по доходам и расходам за последние N месяцев.
        
        Использует эффективные агрегации Django ORM вместо выгрузки всех данных в Python.
        
        Args:
            user: Пользователь, для которого формируется отчет
            months: Количество месяцев для анализа (по умолчанию 12)
        
        Returns:
            QuerySet с аннотированными данными по месяцам
        """
        # Вычисляем дату начала периода (N месяцев назад)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=months * 30)
        
        # Получаем транзакции пользователя за период
        transactions = Transaction.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Группируем по месяцам и типу категории, считаем суммы
        monthly_data = transactions.annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total_income=Coalesce(
                Sum('amount', filter=Q(category__type=Category.INCOME)),
                Value(0, output_field=DecimalField(max_digits=10, decimal_places=2))
            ),
            total_expense=Coalesce(
                Sum('amount', filter=Q(category__type=Category.EXPENSE)),
                Value(0, output_field=DecimalField(max_digits=10, decimal_places=2))
            )
        ).order_by('month')
        
        return monthly_data
    
    @staticmethod
    def get_category_summary(user, start_date=None, end_date=None):
        """
        Получить сводку по категориям за указанный период.
        
        Args:
            user: Пользователь
            start_date: Начало периода (опционально)
            end_date: Конец периода (опционально)
        
        Returns:
            QuerySet с агрегированными данными по категориям
        """
        transactions = Transaction.objects.filter(user=user)
        
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
        
        category_summary = transactions.values(
            'category__name',
            'category__type'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        return category_summary

