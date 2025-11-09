"""
Модели для учета времени (Timesheet) и биллинга.
"""
from django.db import models
from django.core.validators import MinValueValidator
from auditlog.registry import auditlog
from core.models import User
from case_management.models import Case


class WorkType(models.Model):
    """Типы работ для учета времени"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Назва'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Опис'
    )
    
    default_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Стандартна ставка',
        help_text='Годинна ставка за замовчуванням'
    )
    
    is_billable = models.BooleanField(
        default=True,
        verbose_name='Оплачувана',
        help_text='Чи включається в рахунок для клієнта'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активний'
    )
    
    class Meta:
        verbose_name = 'Тип роботи'
        verbose_name_plural = 'Типи робіт'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TimeEntry(models.Model):
    """
    Запись учета времени (Time Entry).
    Адвокат фиксирует время, потраченное на дело.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='time_entries',
        verbose_name='Адвокат'
    )
    
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='time_entries',
        verbose_name='Справа'
    )
    
    work_type = models.ForeignKey(
        WorkType,
        on_delete=models.PROTECT,
        related_name='time_entries',
        verbose_name='Тип роботи'
    )
    
    date = models.DateField(
        verbose_name='Дата'
    )
    
    start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Час початку'
    )
    
    end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Час завершення'
    )
    
    duration_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Тривалість (годин)',
        help_text='Кількість відпрацьованих годин'
    )
    
    description = models.TextField(
        verbose_name='Опис роботи',
        help_text='Детальний опис виконаної роботи'
    )
    
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Годинна ставка',
        help_text='Ставка для розрахунку вартості'
    )
    
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        verbose_name='Загальна сума'
    )
    
    is_billable = models.BooleanField(
        default=True,
        verbose_name='Оплачувана'
    )
    
    is_billed = models.BooleanField(
        default=False,
        verbose_name='Виставлена в рахунку',
        help_text='Чи включено цю роботу в виставлений рахунок'
    )
    
    invoice = models.ForeignKey(
        'billing.Invoice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='time_entries',
        verbose_name='Рахунок'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Внутрішні нотатки',
        help_text='Нотатки для внутрішнього використання (не відображаються клієнту)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')
    
    class Meta:
        verbose_name = 'Запис обліку часу'
        verbose_name_plural = 'Записи обліку часу'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['case', 'date']),
            models.Index(fields=['is_billed']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.case.case_number} ({self.duration_hours}h)"
    
    def save(self, *args, **kwargs):
        # Автоматический расчет общей суммы
        self.total_amount = self.duration_hours * self.hourly_rate
        super().save(*args, **kwargs)
    
    def calculate_duration_from_times(self):
        """Расчет продолжительности на основе start_time и end_time"""
        if self.start_time and self.end_time:
            from datetime import datetime, timedelta
            
            start = datetime.combine(self.date, self.start_time)
            end = datetime.combine(self.date, self.end_time)
            
            if end < start:
                # Если end_time меньше start_time, предполагаем, что работа перешла на следующий день
                end += timedelta(days=1)
            
            duration = end - start
            self.duration_hours = round(duration.total_seconds() / 3600, 2)


class Timer(models.Model):
    """
    Активный таймер для отслеживания времени в реальном времени.
    Позволяет адвокату запускать/останавливать таймер для текущей работы.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='active_timer',
        verbose_name='Адвокат'
    )
    
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        verbose_name='Справа'
    )
    
    work_type = models.ForeignKey(
        WorkType,
        on_delete=models.PROTECT,
        verbose_name='Тип роботи'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Опис роботи'
    )
    
    start_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Час початку'
    )
    
    is_paused = models.BooleanField(
        default=False,
        verbose_name='Призупинено'
    )
    
    paused_duration = models.DurationField(
        default='0',
        verbose_name='Тривалість паузи',
        help_text='Загальна тривалість всіх пауз'
    )
    
    class Meta:
        verbose_name = 'Активний таймер'
        verbose_name_plural = 'Активні таймери'
    
    def __str__(self):
        return f"Таймер {self.user.get_full_name()} - {self.case.case_number}"
    
    def get_elapsed_time(self):
        """Получить прошедшее время (за вычетом пауз)"""
        from django.utils import timezone
        
        total_time = timezone.now() - self.start_time
        working_time = total_time - self.paused_duration
        return working_time
    
    def stop_and_create_entry(self):
        """Остановить таймер и создать запись учета времени"""
        from django.utils import timezone
        
        working_time = self.get_elapsed_time()
        duration_hours = round(working_time.total_seconds() / 3600, 2)
        
        # Создание TimeEntry
        time_entry = TimeEntry.objects.create(
            user=self.user,
            case=self.case,
            work_type=self.work_type,
            date=timezone.now().date(),
            start_time=self.start_time.time(),
            end_time=timezone.now().time(),
            duration_hours=duration_hours,
            description=self.description,
            hourly_rate=self.user.hourly_rate or self.work_type.default_rate,
            is_billable=self.work_type.is_billable
        )
        
        # Удаление таймера
        self.delete()
        
        return time_entry


# Регистрация моделей для аудита
auditlog.register(TimeEntry)

