"""
Модели для биллинга (выставление счетов, акты оказанных услуг).
"""
from django.db import models
from django.core.validators import MinValueValidator
from auditlog.registry import auditlog
from core.models import User, Client
from case_management.models import Case


class Invoice(models.Model):
    """
    Счет-фактура (Рахунок) и Акт оказанных услуг.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Чернетка'),
        ('sent', 'Надіслано'),
        ('paid', 'Оплачено'),
        ('cancelled', 'Скасовано'),
    ]
    
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Номер рахунку'
    )
    
    case = models.ForeignKey(
        Case,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='Справа'
    )
    
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='Клієнт'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Статус'
    )
    
    issue_date = models.DateField(
        verbose_name='Дата виставлення'
    )
    
    due_date = models.DateField(
        verbose_name='Термін оплати'
    )
    
    paid_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата оплати'
    )
    
    # Финансовые данные
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Сума без ПДВ'
    )
    
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20.00,
        verbose_name='Ставка ПДВ (%)',
        help_text='Стандартна ставка ПДВ в Україні - 20%'
    )
    
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False,
        verbose_name='Сума ПДВ'
    )
    
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False,
        verbose_name='Загальна сума'
    )
    
    # Описание услуг
    description = models.TextField(
        blank=True,
        verbose_name='Опис послуг'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Примітки',
        help_text='Додаткова інформація для клієнта'
    )
    
    # Реквизиты исполнителя
    lawyer_name = models.CharField(
        max_length=255,
        verbose_name='ПІБ адвоката'
    )
    
    lawyer_certificate = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Свідоцтво про право на зайняття адвокатською діяльністю'
    )
    
    lawyer_bank_account = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Банківський рахунок адвоката'
    )
    
    # Системные поля
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices',
        verbose_name='Створив'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')
    
    class Meta:
        verbose_name = 'Рахунок'
        verbose_name_plural = 'Рахунки'
        ordering = ['-issue_date', '-invoice_number']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['status']),
            models.Index(fields=['issue_date']),
        ]
    
    def __str__(self):
        return f"Рахунок № {self.invoice_number} від {self.issue_date.strftime('%d.%m.%Y')}"
    
    def save(self, *args, **kwargs):
        # Автоматический расчет налогов и итоговой суммы
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        self.total = self.subtotal + self.tax_amount
        super().save(*args, **kwargs)
    
    def calculate_from_time_entries(self):
        """
        Рассчитать сумму на основе записей учета времени.
        """
        from time_tracking.models import TimeEntry
        
        time_entries = TimeEntry.objects.filter(
            case=self.case,
            is_billable=True,
            is_billed=False
        )
        
        self.subtotal = sum(entry.total_amount for entry in time_entries)
        self.save()
        
        # Связываем записи времени с счетом
        time_entries.update(invoice=self, is_billed=True)
    
    def mark_as_paid(self, paid_date=None):
        """Отметить счет как оплаченный"""
        from django.utils import timezone
        
        self.status = 'paid'
        self.paid_date = paid_date or timezone.now().date()
        self.save()


class InvoiceItem(models.Model):
    """
    Позиция счета (для детализации услуг).
    """
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Рахунок'
    )
    
    description = models.CharField(
        max_length=255,
        verbose_name='Опис послуги'
    )
    
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        validators=[MinValueValidator(0.01)],
        verbose_name='Кількість',
        help_text='Кількість годин або одиниць послуги'
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Ціна за одиницю'
    )
    
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        verbose_name='Всього'
    )
    
    order = models.IntegerField(
        default=0,
        verbose_name='Порядок'
    )
    
    class Meta:
        verbose_name = 'Позиція рахунку'
        verbose_name_plural = 'Позиції рахунку'
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.description} - {self.total} грн"
    
    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Платеж от клиента.
    """
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Готівка'),
        ('bank_transfer', 'Банківський переказ'),
        ('card', 'Картка'),
        ('other', 'Інше'),
    ]
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Рахунок'
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Сума'
    )
    
    payment_date = models.DateField(
        verbose_name='Дата платежу'
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Спосіб оплати'
    )
    
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Номер платіжного документа'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Примітки'
    )
    
    received_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Отримав'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Платіж'
        verbose_name_plural = 'Платежі'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Платіж {self.amount} грн ({self.payment_date.strftime('%d.%m.%Y')})"


# Регистрация моделей для аудита
auditlog.register(Invoice)
auditlog.register(Payment)

