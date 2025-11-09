"""
Celery configuration for law_crm project.
Используется для асинхронных задач (уведомления, интеграция с ЕГРСР).
"""
import os
from celery import Celery
from celery.schedules import crontab

# Установка модуля настроек Django по умолчанию для celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'law_crm.settings')

app = Celery('law_crm')

# Использование строки здесь означает, что работник не должен сериализовать
# объект конфигурации для дочерних процессов.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматический поиск задач во всех приложениях Django
app.autodiscover_tasks()

# Периодические задачи
app.conf.beat_schedule = {
    'check-case-deadlines-daily': {
        'task': 'case_management.tasks.check_case_deadlines',
        'schedule': crontab(hour=9, minute=0),  # Каждый день в 9:00
    },
    'sync-egrsr-cases-daily': {
        'task': 'court_integrations.tasks.sync_egrsr_cases',
        'schedule': crontab(hour=22, minute=0),  # Каждый день в 22:00
    },
}


@app.task(bind=True)
def debug_task(self):
    """Тестовая задача для отладки"""
    print(f'Request: {self.request!r}')

