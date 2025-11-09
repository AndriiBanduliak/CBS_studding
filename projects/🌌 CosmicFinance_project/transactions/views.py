from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Category, Transaction
from .serializers import CategorySerializer, TransactionSerializer
from .filters import TransactionFilter
from .services import TransactionAnalyticsService


class CategoryListCreateView(generics.ListCreateAPIView):
    """
    API эндпоинт для списка и создания категорий.
    
    GET: Получить список всех категорий текущего пользователя
    POST: Создать новую категорию
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает только категории текущего пользователя.
        """
        return Category.objects.filter(user=self.request.user)


class TransactionListCreateView(generics.ListCreateAPIView):
    """
    API эндпоинт для списка и создания транзакций.
    
    GET: Получить список всех транзакций текущего пользователя с пагинацией и фильтрацией
    POST: Создать новую транзакцию
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TransactionFilter
    
    def get_queryset(self):
        """
        Возвращает только транзакции текущего пользователя.
        """
        return Transaction.objects.filter(user=self.request.user).select_related('category')


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API эндпоинт для получения, обновления и удаления отдельной транзакции.
    
    GET: Получить детали транзакции
    PUT/PATCH: Обновить транзакцию
    DELETE: Удалить транзакцию
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает только транзакции текущего пользователя.
        """
        return Transaction.objects.filter(user=self.request.user).select_related('category')


class MonthlySummaryView(APIView):
    """
    API эндпоинт для получения месячной статистики.
    
    GET: Получить сводку по доходам и расходам за последний год по месяцам
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Возвращает аналитику по месяцам с использованием эффективных агрегаций ORM.
        """
        # Получаем количество месяцев из параметров запроса (по умолчанию 12)
        months = int(request.query_params.get('months', 12))
        
        # Используем сервисный слой для получения данных
        monthly_data = TransactionAnalyticsService.get_monthly_summary(
            user=request.user,
            months=months
        )
        
        # Форматируем результат
        result = [
            {
                'month': item['month'].strftime('%Y-%m'),
                'total_income': float(item['total_income'] or 0),
                'total_expense': float(item['total_expense'] or 0),
            }
            for item in monthly_data
        ]
        
        return Response(result, status=status.HTTP_200_OK)


class CategorySummaryView(APIView):
    """
    API эндпоинт для получения статистики по категориям.
    
    GET: Получить сводку по категориям за указанный период
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Возвращает аналитику по категориям.
        """
        # Получаем параметры фильтрации
        start_date = request.query_params.get('date_from')
        end_date = request.query_params.get('date_to')
        
        # Используем сервисный слой для получения данных
        category_data = TransactionAnalyticsService.get_category_summary(
            user=request.user,
            start_date=start_date,
            end_date=end_date
        )
        
        # Форматируем результат
        result = [
            {
                'category': item['category__name'],
                'type': item['category__type'],
                'total': float(item['total']),
            }
            for item in category_data
        ]
        
        return Response(result, status=status.HTTP_200_OK)


class DeleteAllDataView(APIView):
    """
    API эндпоинт для удаления всех данных пользователя.
    
    DELETE: Удалить все категории и транзакции текущего пользователя
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        """
        Удаляет все категории и транзакции текущего пользователя.
        """
        user = request.user
        
        # Подсчитываем количество записей перед удалением
        categories_count = Category.objects.filter(user=user).count()
        transactions_count = Transaction.objects.filter(user=user).count()
        
        # Удаляем транзакции (они зависят от категорий)
        Transaction.objects.filter(user=user).delete()
        
        # Удаляем категории
        Category.objects.filter(user=user).delete()
        
        return Response({
            'message': 'Все данные успешно удалены.',
            'deleted_categories': categories_count,
            'deleted_transactions': transactions_count
        }, status=status.HTTP_200_OK)

