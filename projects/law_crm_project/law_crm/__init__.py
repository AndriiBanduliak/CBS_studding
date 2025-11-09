# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.

# Celery import (опционально для локальной версии)
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery не установлен - работаем без него
    pass

