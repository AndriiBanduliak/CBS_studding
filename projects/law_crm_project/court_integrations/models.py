"""
Модели для интеграции с ЕГРСР и Электронным Судом Украины.
"""
from django.db import models
from case_management.models import Case


class EGRSRSync(models.Model):
    """
    История синхронизации с ЕГРСР (Единый государственный реестр судебных решений).
    """
    
    STATUS_CHOICES = [
        ('success', 'Успішно'),
        ('failed', 'Помилка'),
        ('partial', 'Частково'),
    ]
    
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='egrsr_syncs',
        verbose_name='Справа'
    )
    
    sync_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата синхронізації'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name='Статус'
    )
    
    records_found = models.IntegerField(
        default=0,
        verbose_name='Знайдено записів'
    )
    
    new_decisions = models.IntegerField(
        default=0,
        verbose_name='Нових рішень'
    )
    
    error_message = models.TextField(
        blank=True,
        verbose_name='Повідомлення про помилку'
    )
    
    response_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Дані відповіді API'
    )
    
    class Meta:
        verbose_name = 'Синхронізація з ЄДРСР'
        verbose_name_plural = 'Синхронізації з ЄДРСР'
        ordering = ['-sync_date']
    
    def __str__(self):
        return f"Синхронізація {self.case.case_number} - {self.sync_date.strftime('%d.%m.%Y %H:%M')}"


class CourtDecision(models.Model):
    """
    Судебное решение из ЕГРСР.
    """
    
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='court_decisions',
        verbose_name='Справа'
    )
    
    decision_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='ID рішення в ЄДРСР'
    )
    
    decision_date = models.DateField(
        verbose_name='Дата рішення'
    )
    
    decision_type = models.CharField(
        max_length=100,
        verbose_name='Тип рішення',
        help_text='Ухвала, Рішення, Постанова тощо'
    )
    
    judge_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='ПІБ судді'
    )
    
    summary = models.TextField(
        blank=True,
        verbose_name='Короткий зміст'
    )
    
    full_text = models.TextField(
        blank=True,
        verbose_name='Повний текст рішення'
    )
    
    pdf_url = models.URLField(
        blank=True,
        verbose_name='URL PDF файлу'
    )
    
    egrsr_url = models.URLField(
        blank=True,
        verbose_name='URL на сайті ЄДРСР'
    )
    
    is_new = models.BooleanField(
        default=True,
        verbose_name='Нове рішення',
        help_text='Чи було рішення переглянуте адвокатом'
    )
    
    imported_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата імпорту'
    )
    
    class Meta:
        verbose_name = 'Судове рішення'
        verbose_name_plural = 'Судові рішення'
        ordering = ['-decision_date']
        indexes = [
            models.Index(fields=['decision_id']),
            models.Index(fields=['case', 'decision_date']),
        ]
    
    def __str__(self):
        return f"{self.decision_type} від {self.decision_date.strftime('%d.%m.%Y')}"

