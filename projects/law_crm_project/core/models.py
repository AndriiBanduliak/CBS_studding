"""
Модели приложения Core.
Содержит пользователей, клиентов и базовые настройки.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from auditlog.registry import auditlog
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    """
    Кастомная модель пользователя с ролями для адвокатского объединения.
    Roles: Адвокат, Помощник, Партнер, Администратор.
    """
    
    ROLE_CHOICES = [
        ('lawyer', 'Адвокат'),
        ('assistant', 'Помічник адвоката'),
        ('partner', 'Партнер'),
        ('admin', 'Адміністратор'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='lawyer',
        verbose_name='Роль'
    )
    
    # Профиль НААУ
    naau_certificate_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Номер свідоцтва НААУ',
        help_text='Номер свідоцтва про право на заняття адвокатською діяльністю'
    )
    
    phone = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name='Телефон'
    )
    
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата народження'
    )
    
    photo = models.ImageField(
        upload_to='users/photos/',
        blank=True,
        null=True,
        verbose_name='Фото'
    )
    
    # Реквизиты для выставления счетов
    bank_account = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Банківський рахунок'
    )
    
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Годинна ставка',
        help_text='Стандартна годинна ставка для розрахунку вартості послуг'
    )
    
    is_active_lawyer = models.BooleanField(
        default=True,
        verbose_name='Активний адвокат',
        help_text='Чи може приймати нові справи'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')
    
    class Meta:
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return self.get_full_name() or self.username
    
    def can_access_case(self, case):
        """Проверка доступа к делу согласно RBAC"""
        if self.role in ['partner', 'admin']:
            return True
        if self.role == 'lawyer':
            return case.lawyers.filter(id=self.id).exists()
        if self.role == 'assistant':
            # Помощник видит дела, где ему предоставлен доступ
            return case.assistants.filter(id=self.id).exists()
        return False


class Client(models.Model):
    """
    Модель Клиента (физическое или юридическое лицо).
    Включает украинскую специфику: РНОКПП (ИНН) / ЕДРПОУ.
    """
    
    CLIENT_TYPE_CHOICES = [
        ('individual', 'Фізична особа'),
        ('legal', 'Юридична особа'),
    ]
    
    client_type = models.CharField(
        max_length=20,
        choices=CLIENT_TYPE_CHOICES,
        verbose_name='Тип клієнта'
    )
    
    # Для физических лиц
    first_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Ім\'я'
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Прізвище'
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='По батькові'
    )
    
    # Для юридических лиц
    company_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Назва організації'
    )
    
    # РНОКПП (ИНН) для физических лиц
    rnokpp = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        unique=True,
        verbose_name='РНОКПП (ІПН)',
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='РНОКПП повинен містити 10 цифр'
            )
        ]
    )
    
    # ЕДРПОУ для юридических лиц
    edrpou = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        unique=True,
        verbose_name='ЄДРПОУ',
        validators=[
            RegexValidator(
                regex=r'^\d{8}$',
                message='ЄДРПОУ повинен містити 8 цифр'
            )
        ]
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name='Email'
    )
    
    phone = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name='Телефон'
    )
    
    phone_additional = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name='Додатковий телефон'
    )
    
    address = models.TextField(
        blank=True,
        verbose_name='Адреса'
    )
    
    passport_data = models.TextField(
        blank=True,
        verbose_name='Паспортні дані',
        help_text='Серія, номер, ким і коли виданий'
    )
    
    # Представитель (для юр. лиц)
    representative_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='ПІБ представника'
    )
    representative_position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Посада представника'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Примітки'
    )
    
    # Ответственный менеджер
    responsible_lawyer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_clients',
        verbose_name='Відповідальний адвокат'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активний'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_clients',
        verbose_name='Створив'
    )
    
    class Meta:
        verbose_name = 'Клієнт'
        verbose_name_plural = 'Клієнти'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['rnokpp']),
            models.Index(fields=['edrpou']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['company_name']),
        ]
    
    def __str__(self):
        if self.client_type == 'individual':
            return f"{self.last_name} {self.first_name} {self.middle_name}".strip()
        return self.company_name
    
    @property
    def full_name(self):
        return str(self)
    
    @property
    def identifier(self):
        """Возвращает РНОКПП или ЕДРПОУ"""
        return self.rnokpp if self.client_type == 'individual' else self.edrpou
    
    def clean(self):
        """Валидация: физ.лицо должно иметь ФИО и РНОКПП, юр.лицо - название и ЕДРПОУ"""
        from django.core.exceptions import ValidationError
        
        if self.client_type == 'individual':
            if not (self.first_name and self.last_name):
                raise ValidationError('Для фізичної особи обов\'язкові Ім\'я та Прізвище')
        elif self.client_type == 'legal':
            if not self.company_name:
                raise ValidationError('Для юридичної особи обов\'язкова Назва організації')


class ConflictCheck(models.Model):
    """
    Модель для проверки конфликта интересов.
    Фиксирует все проверки перед принятием дела.
    """
    
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='conflict_checks',
        verbose_name='Клієнт'
    )
    
    opposing_party_name = models.CharField(
        max_length=255,
        verbose_name='ПІБ/Назва протилежної сторони'
    )
    
    opposing_party_identifier = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='РНОКПП/ЄДРПОУ протилежної сторони'
    )
    
    has_conflict = models.BooleanField(
        default=False,
        verbose_name='Виявлено конфлікт'
    )
    
    conflict_details = models.TextField(
        blank=True,
        verbose_name='Деталі конфлікту'
    )
    
    checked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Перевірив'
    )
    
    checked_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата перевірки')
    
    class Meta:
        verbose_name = 'Перевірка конфлікту інтересів'
        verbose_name_plural = 'Перевірки конфліктів інтересів'
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"Перевірка для {self.client} - {self.opposing_party_name}"


# Регистрация моделей для аудита
auditlog.register(User)
auditlog.register(Client)
auditlog.register(ConflictCheck)

