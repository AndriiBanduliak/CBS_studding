#!/usr/bin/env python
"""
Простой WSGI сервер БЕЗ проверки миграций
Использует waitress для запуска Django приложения
"""
import os
import sys

# Установить переменные окружения ДО импорта Django
os.environ['PYTHONUTF8'] = '1'
os.environ['PGPASSFILE'] = 'nul'
os.environ['PGSERVICEFILE'] = 'nul'
os.environ['PGSYSCONFDIR'] = 'nul'
os.environ['PGCLIENTENCODING'] = 'UTF8'

temp_dir = os.environ.get('TEMP', 'C:\\Windows\\Temp')
os.environ['APPDATA'] = temp_dir
os.environ['LOCALAPPDATA'] = temp_dir
os.environ['HOME'] = temp_dir
os.environ['USERPROFILE'] = temp_dir

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'law_crm.settings')

print("[INFO] Using pg8000 pure Python PostgreSQL driver")
print("[INFO] No libpq dependency - no encoding issues!")
print()

# Импортируем Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

if __name__ == '__main__':
    try:
        from waitress import serve
        print("=" * 60)
        print("Law CRM Server")
        print("=" * 60)
        print()
        print("Starting server...")
        print("✓ Web interface: http://127.0.0.1:8000")
        print("✓ Admin panel:   http://127.0.0.1:8000/admin")
        print()
        print("Press Ctrl+C to stop")
        print()
        serve(application, host='127.0.0.1', port=8000, threads=4)
    except ImportError:
        print("Installing waitress...")
        os.system('pip install waitress')
        from waitress import serve
        serve(application, host='127.0.0.1', port=8000, threads=4)

