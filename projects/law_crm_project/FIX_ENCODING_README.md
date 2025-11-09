# Исправление проблемы кодировки PostgreSQL на Windows

## Проблема
`UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc2 in position 61` при подключении к PostgreSQL.

## Причина
Когда имя пользователя Windows содержит кириллицу (например, `C:\Users\andrj\...`), библиотека libpq (используемая psycopg2) пытается прочитать конфигурационные файлы из профиля пользователя и не может правильно декодировать путь.

## Решение

### Изменения в коде:

1. **settings.py** - Изменен `DB_HOST` с `localhost` на `127.0.0.1`
2. **simple_server.py** - Создан простой WSGI сервер на базе `waitress` который:
   - Устанавливает переменные окружения ДО загрузки Django
   - НЕ проверяет миграции при запуске (в отличие от `runserver`)
   - Работает стабильно без проблем кодировки

3. **start_server.bat** / **run.bat** - Обновлены для использования `simple_server.py`
4. **requirements_windows.txt** - Добавлен `waitress` WSGI сервер

### Как запускать сервер:

#### Способ 1: Через bat-файл (РЕКОМЕНДУЕТСЯ)
```cmd
start_server.bat
```

#### Способ 2: Вручную в CMD
```cmd
venv\Scripts\python.exe -X utf8=1 simple_server.py
```

#### Способ 3: Через виртуальное окружение
```cmd
venv\Scripts\activate
python -X utf8=1 simple_server.py
```

### Важно:
- **Сервер использует `waitress` вместо Django `runserver`**
- `waitress` - production-ready WSGI сервер для Windows
- Не проверяет миграции при запуске (быстрее запускается)
- Стабильно работает без проблем кодировки

### Для других команд Django:

Для выполнения других команд (migrate, createsuperuser и т.д.) используйте `run_django.py`:

```cmd
venv\Scripts\python.exe -X utf8=1 run_django.py migrate
venv\Scripts\python.exe -X utf8=1 run_django.py createsuperuser
venv\Scripts\python.exe -X utf8=1 run_django.py check
```

### Адреса после запуска:
- Web-интерфейс: http://127.0.0.1:8000
- Админ-панель: http://127.0.0.1:8000/admin

## Техническая информация

### Использованные решения:

1. **Замена Django runserver на waitress**
   - Django `runserver` всегда проверяет миграции при старте
   - При проверке миграций psycopg2 читает конфигурационные файлы
   - `waitress` - чистый WSGI сервер без проверок
   
2. **Установленные переменные окружения в simple_server.py:**
   - `PYTHONUTF8=1` - Принудительный UTF-8 режим Python
   - `APPDATA=%TEMP%` - Перенаправление в TEMP (без кириллицы)
   - `LOCALAPPDATA=%TEMP%` - Перенаправление локальных данных
   - `HOME=%TEMP%` - Домашняя директория без кириллицы
   - `USERPROFILE=%TEMP%` - Профиль пользователя
   - `PGPASSFILE=nul` - Отключение чтения .pgpass
   - `PGSERVICEFILE=nul` - Отключение чтения pg_service.conf
   - `PGSYSCONFDIR=nul` - Отключение системных конфигов PostgreSQL
   - `PGCLIENTENCODING=UTF8` - Принудительная UTF-8 кодировка

3. **Флаги Python:**
   - `-X utf8=1` - UTF-8 режим для всех операций

4. **Настройки БД:**
   - `DB_HOST=127.0.0.1` вместо `localhost` (избегает DNS разрешения)

