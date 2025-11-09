"""
Celery задачи для case_management.
Проверка сроков, отправка уведомлений.
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import Case, CaseEvent


@shared_task
def check_case_deadlines():
    """
    Ежедневная проверка процессуальных сроков и отправка уведомлений.
    Запускается через Celery Beat каждый день в 9:00.
    """
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    three_days = today + timedelta(days=3)
    
    # Проверка дел с приближающимися сроками (за 3 дня)
    cases_with_deadline = Case.objects.filter(
        deadline_date__lte=three_days,
        deadline_date__gte=today,
        status='in_progress'
    ).select_related('responsible_lawyer', 'client').prefetch_related('lawyers')
    
    for case in cases_with_deadline:
        days_left = (case.deadline_date - today).days
        
        # Отправка уведомления ответственному адвокату
        if case.responsible_lawyer and case.responsible_lawyer.email:
            subject = f'Нагадування: процесуальний строк у справі {case.case_number}'
            message = f'''
Доброго дня!

Нагадуємо, що у справі "{case.title}" (№ {case.case_number}) 
залишилось {days_left} днів до критичного процесуального строку.

Дата строку: {case.deadline_date.strftime('%d.%m.%Y')}
Клієнт: {case.client.full_name}

Будь ласка, перевірте готовність необхідних документів.

---
Law CRM
            '''
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [case.responsible_lawyer.email],
                fail_silently=True,
            )
    
    # Проверка предстоящих событий (заседаний)
    upcoming_events = CaseEvent.objects.filter(
        event_date__date__lte=tomorrow,
        event_date__date__gte=today,
        is_completed=False,
        reminder_sent=False
    ).select_related('case', 'case__responsible_lawyer')
    
    for event in upcoming_events:
        case = event.case
        
        if case.responsible_lawyer and case.responsible_lawyer.email:
            subject = f'Нагадування: {event.get_event_type_display()} - {event.title}'
            message = f'''
Доброго дня!

Нагадуємо про заплановану подію:

Тип: {event.get_event_type_display()}
Назва: {event.title}
Дата і час: {event.event_date.strftime('%d.%m.%Y о %H:%M')}
Місце: {event.location or "Не вказано"}

Справа: {case.title} (№ {case.case_number})
Клієнт: {case.client.full_name}

---
Law CRM
            '''
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [case.responsible_lawyer.email],
                fail_silently=True,
            )
            
            # Отмечаем, что уведомление отправлено
            event.reminder_sent = True
            event.save()
    
    return f'Checked {len(cases_with_deadline)} cases and {len(upcoming_events)} events'


@shared_task
def send_case_notification(case_id, message_text):
    """
    Отправка уведомления по делу.
    """
    try:
        case = Case.objects.get(id=case_id)
        
        # Отправка уведомления всем адвокатам по делу
        emails = []
        if case.responsible_lawyer and case.responsible_lawyer.email:
            emails.append(case.responsible_lawyer.email)
        
        for lawyer in case.lawyers.all():
            if lawyer.email and lawyer.email not in emails:
                emails.append(lawyer.email)
        
        if emails:
            send_mail(
                f'Оновлення по справі {case.case_number}',
                message_text,
                settings.EMAIL_HOST_USER,
                emails,
                fail_silently=True,
            )
        
        return f'Notification sent to {len(emails)} recipients'
    except Case.DoesNotExist:
        return f'Case {case_id} not found'

