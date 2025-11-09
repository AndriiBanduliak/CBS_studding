#!/usr/bin/env python
"""
Финальное решение: Запуск через subprocess с правильными переменными окружения
Устанавливает переменные окружения ДО запуска Python процесса
"""
import os
import sys
import subprocess

# Подготавливаем переменные окружения
env = os.environ.copy()

# Устанавливаем все необходимые переменные
env['PYTHONUTF8'] = '1'
env['PGPASSFILE'] = 'nul'
env['PGSERVICEFILE'] = 'nul'
env['PGSYSCONFDIR'] = 'nul'
env['PGCLIENTENCODING'] = 'UTF8'

# Переопределяем пути пользователя
temp_dir = env.get('TEMP', 'C:\\Windows\\Temp')
env['APPDATA'] = temp_dir
env['LOCALAPPDATA'] = temp_dir
env['HOME'] = temp_dir
env['USERPROFILE'] = temp_dir
env['HOMEDRIVE'] = 'C:'
env['HOMEPATH'] = '\\Windows\\Temp'

# Устанавливаем DATABASE_URL напрямую
env['DATABASE_URL'] = 'postgresql://law_crm_user:password123@127.0.0.1:5432/law_crm_db?sslmode=disable&client_encoding=utf8'

print("=" * 70)
print("Law CRM Server Launcher")
print("=" * 70)
print()
print("Setting environment variables...")
print(f"  PYTHONUTF8: {env['PYTHONUTF8']}")
print(f"  APPDATA: {env['APPDATA']}")
print(f"  HOME: {env['HOME']}")
print(f"  DATABASE_URL: postgresql://law_crm_user:***@127.0.0.1:5432/law_crm_db")
print()
print("Starting server...")
print()

# Запускаем simple_server.py в отдельном процессе с новыми переменными
cmd = [
    sys.executable,  # Путь к текущему Python
    '-X', 'utf8=1',  # Флаг UTF-8
    'simple_server.py'
]

try:
    # Запускаем процесс
    process = subprocess.Popen(
        cmd,
        env=env,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    print(f"✓ Server process started (PID: {process.pid})")
    print()
    print("=" * 70)
    print("Server should be running at:")
    print("  Web interface: http://127.0.0.1:8000")
    print("  Admin panel:   http://127.0.0.1:8000/admin")
    print("=" * 70)
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    # Ждем завершения процесса
    process.wait()
    
except KeyboardInterrupt:
    print("\n\nShutting down...")
    process.terminate()
    process.wait()
    print("Server stopped.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

