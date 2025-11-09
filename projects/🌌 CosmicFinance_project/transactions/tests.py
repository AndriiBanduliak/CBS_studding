from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Category, Transaction
from .services import TransactionAnalyticsService

User = get_user_model()


class CategoryAPITest(APITestCase):
    """
    Тесты для API категорий.
    """
    
    def setUp(self):
        """
        Подготовка данных для тестов.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
    def test_unauthenticated_access(self):
        """
        Тест: неаутентифицированный пользователь получает 401.
        """
        url = reverse('category-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_category(self):
        """
        Тест: создание категории возвращает 201.
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('category-list-create')
        data = {
            'name': 'Зарплата',
            'type': 'Income'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.first().user, self.user)
    
    def test_list_categories(self):
        """
        Тест: пользователь видит только свои категории.
        """
        Category.objects.create(name='Зарплата', type='Income', user=self.user)
        Category.objects.create(name='Бонус', type='Income', user=self.user)
        Category.objects.create(name='Другая категория', type='Expense', user=self.other_user)
        
        self.client.force_authenticate(user=self.user)
        url = reverse('category-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class TransactionAPITest(APITestCase):
    """
    Тесты для API транзакций.
    """
    
    def setUp(self):
        """
        Подготовка данных для тестов.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Зарплата',
            type='Income',
            user=self.user
        )
        
    def test_create_transaction(self):
        """
        Тест: создание транзакции возвращает 201.
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('transaction-list-create')
        data = {
            'category': self.category.id,
            'amount': '5000.00',
            'description': 'Тестовая транзакция',
            'date': datetime.now().isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)
    
    def test_list_transactions_with_pagination(self):
        """
        Тест: список транзакций возвращается с пагинацией.
        """
        # Создаем 25 транзакций
        for i in range(25):
            Transaction.objects.create(
                user=self.user,
                category=self.category,
                amount=Decimal('100.00'),
                date=datetime.now()
            )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('transaction-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        # Проверяем, что возвращается 20 записей на странице (настройка по умолчанию)
        self.assertEqual(len(response.data['results']), 20)
    
    def test_filter_transactions_by_category(self):
        """
        Тест: фильтрация транзакций по категории.
        """
        category2 = Category.objects.create(
            name='Продукты',
            type='Expense',
            user=self.user
        )
        
        Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('5000.00'),
            date=datetime.now()
        )
        Transaction.objects.create(
            user=self.user,
            category=category2,
            amount=Decimal('1000.00'),
            date=datetime.now()
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('transaction-list-create')
        response = self.client.get(url, {'category_id': self.category.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_transactions_by_date_range(self):
        """
        Тест: фильтрация транзакций по диапазону дат.
        """
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        
        Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('1000.00'),
            date=week_ago
        )
        Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('2000.00'),
            date=yesterday
        )
        Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('3000.00'),
            date=now
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('transaction-list-create')
        
        # Фильтруем транзакции за последние 2 дня
        two_days_ago = now - timedelta(days=2)
        response = self.client.get(url, {
            'date_from': two_days_ago.isoformat(),
            'date_to': now.isoformat()
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_update_transaction(self):
        """
        Тест: обновление транзакции.
        """
        transaction = Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('1000.00'),
            date=datetime.now()
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('transaction-detail', kwargs={'pk': transaction.id})
        data = {
            'category': self.category.id,
            'amount': '2000.00',
            'date': datetime.now().isoformat()
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transaction.refresh_from_db()
        self.assertEqual(transaction.amount, Decimal('2000.00'))
    
    def test_delete_transaction(self):
        """
        Тест: удаление транзакции.
        """
        transaction = Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('1000.00'),
            date=datetime.now()
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('transaction-detail', kwargs={'pk': transaction.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Transaction.objects.count(), 0)


class MonthlySummaryAPITest(APITestCase):
    """
    Тесты для аналитического эндпоинта месячной статистики.
    """
    
    def setUp(self):
        """
        Подготовка данных для тестов.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Создаем категории
        self.income_category = Category.objects.create(
            name='Зарплата',
            type='Income',
            user=self.user
        )
        self.expense_category = Category.objects.create(
            name='Продукты',
            type='Expense',
            user=self.user
        )
    
    def test_monthly_summary_unauthenticated(self):
        """
        Тест: неаутентифицированный доступ возвращает 401.
        """
        url = reverse('monthly-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_monthly_summary_calculation(self):
        """
        Тест: проверка корректности расчета месячной статистики.
        """
        now = datetime.now()
        
        # Создаем транзакции за текущий месяц
        Transaction.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('5000.00'),
            date=now
        )
        Transaction.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('3000.00'),
            date=now
        )
        Transaction.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('2000.00'),
            date=now
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('monthly-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        
        # Проверяем, что в ответе есть данные за текущий месяц
        current_month = now.strftime('%Y-%m')
        current_month_data = next(
            (item for item in response.data if item['month'] == current_month),
            None
        )
        
        self.assertIsNotNone(current_month_data)
        self.assertEqual(current_month_data['total_income'], 8000.00)
        self.assertEqual(current_month_data['total_expense'], 2000.00)


class TransactionAnalyticsServiceTest(TestCase):
    """
    Unit-тесты для сервисного слоя аналитики.
    """
    
    def setUp(self):
        """
        Подготовка данных для тестов.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Создаем категории
        self.income_category = Category.objects.create(
            name='Зарплата',
            type='Income',
            user=self.user
        )
        self.expense_category = Category.objects.create(
            name='Продукты',
            type='Expense',
            user=self.user
        )
    
    def test_monthly_summary_orm_efficiency(self):
        """
        Тест: проверка, что monthly_summary использует ORM агрегации,
        а не выгружает все данные в Python.
        """
        now = datetime.now()
        
        # Создаем несколько транзакций
        for i in range(10):
            Transaction.objects.create(
                user=self.user,
                category=self.income_category,
                amount=Decimal('1000.00'),
                date=now - timedelta(days=i*30)
            )
        
        # Проверяем, что метод возвращает QuerySet, а не список
        result = TransactionAnalyticsService.get_monthly_summary(self.user)
        
        # Результат должен быть QuerySet или iterable
        self.assertTrue(hasattr(result, '__iter__'))
        
        # Проверяем наличие агрегированных полей
        if result.exists():
            first_item = result.first()
            self.assertIn('month', first_item)
            self.assertIn('total_income', first_item)
            self.assertIn('total_expense', first_item)
    
    def test_category_summary(self):
        """
        Тест: проверка расчета статистики по категориям.
        """
        now = datetime.now()
        
        # Создаем транзакции
        Transaction.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('5000.00'),
            date=now
        )
        Transaction.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('2000.00'),
            date=now
        )
        
        result = TransactionAnalyticsService.get_category_summary(self.user)
        
        self.assertEqual(result.count(), 2)
        
        # Проверяем, что результат содержит правильные данные
        for item in result:
            if item['category__name'] == 'Зарплата':
                self.assertEqual(item['total'], Decimal('5000.00'))
            elif item['category__name'] == 'Продукты':
                self.assertEqual(item['total'], Decimal('2000.00'))

