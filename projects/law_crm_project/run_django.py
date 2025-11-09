#!/usr/bin/env python
"""
Wrapper для запуска Django с правильными переменными окружения
Решает проблему кодировки на Windows с non-ASCII путями
"""
import os
import sys

# КРИТИЧНО: Установить ВСЕ переменные окружения ДО любых импортов
os.environ['PYTHONUTF8'] = '1'
os.environ['PGPASSFILE'] = 'nul'
os.environ['PGSERVICEFILE'] = 'nul'
os.environ['PGSYSCONFDIR'] = 'nul'
os.environ['PGCLIENTENCODING'] = 'UTF8'

# Переопределяем все пути к профилю пользователя на TEMP (без кириллицы)
temp_dir = os.environ.get('TEMP', 'C:\\Windows\\Temp')
os.environ['APPDATA'] = temp_dir
os.environ['LOCALAPPDATA'] = temp_dir
os.environ['HOME'] = temp_dir
os.environ['USERPROFILE'] = temp_dir
os.environ['HOMEDRIVE'] = 'C:'
os.environ['HOMEPATH'] = '\\Windows\\Temp'

# Принудительная загрузка psycopg2 с правильными настройками
try:
    import psycopg2
    import psycopg2.extensions
    # Установить клиентскую кодировку для psycopg2
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
    
    # Монкипатч для использования connection string вместо параметров
    original_connect = psycopg2.connect
    
    def patched_connect(*args, **kwargs):
        # Если передаются отдельные параметры, преобразуем в DSN
        if 'database' in kwargs or 'dbname' in kwargs:
            dbname = kwargs.pop('database', kwargs.pop('dbname', 'law_crm_db'))
            user = kwargs.pop('user', 'law_crm_user')
            password = kwargs.pop('password', 'password123')
            host = kwargs.pop('host', '127.0.0.1')
            port = kwargs.pop('port', '5432')
            
            # Создаем DSN строку
            dsn = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=disable&client_encoding=utf8"
            return original_connect(dsn, **kwargs)
        return original_connect(*args, **kwargs)
    
    psycopg2.connect = patched_connect
except Exception as e:
    print(f"Warning: Could not patch psycopg2: {e}")

# Теперь можно запустить manage.py
if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'law_crm.settings')
    
    # Для runserver добавляем --noreload и --skip-checks если еще не указано
    if 'runserver' in sys.argv:
        if '--noreload' not in sys.argv:
            sys.argv.append('--noreload')
            print("INFO: Running with --noreload to preserve environment variables")
        if '--skip-checks' not in sys.argv:
            sys.argv.append('--skip-checks')
            print("INFO: Running with --skip-checks to avoid migration check on startup")
    
    # Передаем аргументы команды
    execute_from_command_line(sys.argv)

