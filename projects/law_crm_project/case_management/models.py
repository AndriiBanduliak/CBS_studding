"""
Модели для управления делами.
Включает FSM для процессуальной воронки, учет ордеров, связь с ЕГРСР.
"""
from django.db import models
from django.core.validators import RegexValidator
from django_fsm import FSMField, transition
from auditlog.registry import auditlog
from core.models import User, Client


class Court(models.Model):
    """Модель суда"""
    
    COURT_TYPE_CHOICES = [
        ('local', 'Місцевий суд'),
        ('appeal', 'Апеляційний суд'),
        ('supreme', 'Верховний Суд'),
        ('economic', 'Господарський суд'),
        ('administrative', 'Адміністративний суд'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Назва суду')
    court_type = models.CharField(
        max_length=20,
        choices=COURT_TYPE_CHOICES,
        verbose_name='Тип суду'
    )
    address = models.TextField(verbose_name='Адреса')
    phone = models.CharField(max_length=50, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    website = models.URLField(blank=True, verbose_name='Веб-сайт')
    
    class Meta:
        verbose_name = 'Суд'
        verbose_name_plural = 'Суди'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Case(models.Model):
    """
    Модель дела с FSM для управления стадиями.
    """
    
    PROCEEDING_TYPE_CHOICES = [
        ('criminal', 'Кримінальне'),
        ('civil', 'Цивільне'),
        ('economic', 'Господарське'),
        ('administrative', 'Адміністративне'),
        ('administrative_offense', 'Про адмінправопорушення'),
    ]
    
    # Базовая информация
    case_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Номер справи',
        help_text='Номер справи в суді'
    )
    
    title = models.CharField(
        max_length=255,
        verbose_name='Назва справи'
    )
    
    description = models.TextField(
        verbose_name='Опис справи',
        help_text='Короткий опис обставин справи'
    )
    
    proceeding_type = models.CharField(
        max_length=30,
        choices=PROCEEDING_TYPE_CHOICES,
        verbose_name='Вид провадження'
    )
    
    # FSM Status Field
    status = FSMField(
        default='new',
        verbose_name='Статус',
        choices=[
            ('new', 'Нова'),
            ('consultation', 'Консультація'),
            ('contract_preparation', 'Підготовка договору'),
            ('in_progress', 'В роботі'),
            ('suspended', 'Зупинено'),
            ('closed_won', 'Закрита (виграна)'),
            ('closed_lost', 'Закрита (програна)'),
            ('closed_settled', 'Закрита (врегульована)'),
            ('archived', 'Архівована'),
        ]
    )
    
    # Клиент и связанные лица
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='cases',
        verbose_name='Клієнт'
    )
    
    opposing_party = models.CharField(
        max_length=255,
        verbose_name='Протилежна сторона'
    )
    
    opposing_party_lawyer = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Адвокат протилежної сторони'
    )
    
    # Суд
    court = models.ForeignKey(
        Court,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cases',
        verbose_name='Суд'
    )
    
    judge = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Суддя'
    )
    
    # Команда адвокатов
    lawyers = models.ManyToManyField(
        User,
        related_name='assigned_cases',
        limit_choices_to={'role__in': ['lawyer', 'partner']},
        verbose_name='Адвокати'
    )
    
    assistants = models.ManyToManyField(
        User,
        related_name='assisted_cases',
        blank=True,
        limit_choices_to={'role': 'assistant'},
        verbose_name='Помічники'
    )
    
    responsible_lawyer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='responsible_cases',
        limit_choices_to={'role__in': ['lawyer', 'partner']},
        verbose_name='Відповідальний адвокат'
    )
    
    # Важные даты
    registration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата відкриття провадження'
    )
    
    first_hearing_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата першого засідання'
    )
    
    next_hearing_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата наступного засідання'
    )
    
    deadline_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Процесуальний строк',
        help_text='Критичний строк для подачі документів/оскарження'
    )
    
    closed_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата закриття справи'
    )
    
    # ЕГРСР integration
    egrsr_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID в ЄДРСР',
        help_text='Ідентифікатор справи в Єдиному державному реєстрі судових рішень'
    )
    
    last_egrsr_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Остання синхронізація з ЄДРСР'
    )
    
    # Финансы
    estimated_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Ціна позову',
        help_text='Сума позовних вимог'
    )
    
    contract_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Сума договору',
        help_text='Гонорар адвоката за договором'
    )
    
    # Дополнительная информация
    notes = models.TextField(
        blank=True,
        verbose_name='Примітки'
    )
    
    is_priority = models.BooleanField(
        default=False,
        verbose_name='Пріоритетна справа'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_cases',
        verbose_name='Створив'
    )
    
    class Meta:
        verbose_name = 'Справа'
        verbose_name_plural = 'Справи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['case_number']),
            models.Index(fields=['status']),
            models.Index(fields=['next_hearing_date']),
            models.Index(fields=['deadline_date']),
        ]
    
    def __str__(self):
        return f"{self.case_number} - {self.title}"
    
    # FSM Transitions
    @transition(field=status, source='new', target='consultation')
    def start_consultation(self):
        """Начать консультацию с клиентом"""
        pass
    
    @transition(field=status, source='consultation', target='contract_preparation')
    def prepare_contract(self):
        """Подготовить договор о правовой помощи"""
        pass
    
    @transition(field=status, source='contract_preparation', target='in_progress')
    def start_work(self):
        """Начать работу по делу"""
        pass
    
    @transition(field=status, source='in_progress', target='suspended')
    def suspend(self):
        """Приостановить дело"""
        pass
    
    @transition(field=status, source='suspended', target='in_progress')
    def resume(self):
        """Возобновить дело"""
        pass
    
    @transition(field=status, source='in_progress', target='closed_won')
    def close_won(self):
        """Закрыть дело (выиграно)"""
        self.closed_date = models.functions.Now()
    
    @transition(field=status, source='in_progress', target='closed_lost')
    def close_lost(self):
        """Закрыть дело (проиграно)"""
        self.closed_date = models.functions.Now()
    
    @transition(field=status, source='in_progress', target='closed_settled')
    def close_settled(self):
        """Закрыть дело (урегулировано)"""
        self.closed_date = models.functions.Now()
    
    @transition(field=status, source=['closed_won', 'closed_lost', 'closed_settled'], 
                target='archived')
    def archive(self):
        """Архивировать дело"""
        pass


class LawyerOrder(models.Model):
    """
    Модель ордера адвоката.
    Согласно украинскому законодательству, адвокат подтверждает свои полномочия ордером.
    """
    
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Справа'
    )
    
    lawyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        limit_choices_to={'role__in': ['lawyer', 'partner']},
        verbose_name='Адвокат'
    )
    
    order_series = models.CharField(
        max_length=10,
        verbose_name='Серія ордера'
    )
    
    order_number = models.CharField(
        max_length=20,
        verbose_name='Номер ордера',
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='Номер ордера повинен містити тільки цифри'
            )
        ]
    )
    
    issue_date = models.DateField(verbose_name='Дата видачі')
    
    issued_by = models.CharField(
        max_length=255,
        default='Адвокатське об\'єднання',
        verbose_name='Ким видано'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активний'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Примітки'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ордер'
        verbose_name_plural = 'Ордери'
        ordering = ['-issue_date']
        unique_together = ['order_series', 'order_number']
    
    def __str__(self):
        return f"Ордер {self.order_series}-{self.order_number} ({self.lawyer.get_full_name()})"


class CaseEvent(models.Model):
    """
    События по делу (заседания, процессуальные действия).
    """
    
    EVENT_TYPE_CHOICES = [
        ('hearing', 'Судове засідання'),
        ('deadline', 'Процесуальний строк'),
        ('filing', 'Подання документів'),
        ('decision', 'Рішення суду'),
        ('meeting', 'Зустріч з клієнтом'),
        ('other', 'Інше'),
    ]
    
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Справа'
    )
    
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        verbose_name='Тип події'
    )
    
    title = models.CharField(
        max_length=255,
        verbose_name='Назва події'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Опис'
    )
    
    event_date = models.DateTimeField(verbose_name='Дата і час події')
    
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Місце проведення'
    )
    
    is_completed = models.BooleanField(
        default=False,
        verbose_name='Завершено'
    )
    
    reminder_sent = models.BooleanField(
        default=False,
        verbose_name='Нагадування надіслано'
    )
    
    result = models.TextField(
        blank=True,
        verbose_name='Результат',
        help_text='Результат події (ухвала, висновок тощо)'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Створив'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Подія у справі'
        verbose_name_plural = 'Події у справі'
        ordering = ['event_date']
        indexes = [
            models.Index(fields=['event_date']),
            models.Index(fields=['is_completed']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.title}"


class CaseNote(models.Model):
    """Заметки по делу"""
    
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='case_notes',
        verbose_name='Справа'
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Автор'
    )
    
    content = models.TextField(verbose_name='Зміст')
    
    is_important = models.BooleanField(
        default=False,
        verbose_name='Важливо'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')
    
    class Meta:
        verbose_name = 'Нотатка'
        verbose_name_plural = 'Нотатки'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Нотатка від {self.created_at.strftime('%d.%m.%Y')}"


# Регистрация моделей для аудита
auditlog.register(Case)
auditlog.register(LawyerOrder)
auditlog.register(CaseEvent)

