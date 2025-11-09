@echo off
REM Упрощенная локальная установка Law CRM на Windows (без Docker)
chcp 65001 >nul
cls

echo ========================================================
echo     Law CRM - Локальна установка (Windows)
echo ========================================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python не встановлено!
    echo.
    echo Завантажте та встановіть Python 3.10+:
    echo https://www.python.org/downloads/
    echo.
    echo ВАЖЛИВО: Поставте галочку "Add Python to PATH"!
    pause
    exit /b 1
)

python --version
echo [OK] Python встановлено
echo.

REM Проверка PostgreSQL
psql --version >nul 2>&1
if errorlevel 1 (
    echo [!] PostgreSQL не знайдено
    echo.
    echo Якщо PostgreSQL не встановлено:
    echo 1. Завантажте: https://www.postgresql.org/download/windows/
    echo 2. Встановіть PostgreSQL 14+
    echo 3. Запам'ятайте пароль для користувача postgres
    echo.
    set /p continue="PostgreSQL встановлено? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
)
echo [OK] PostgreSQL встановлено
echo.

echo ========================================================
echo КРОК 1: Створення бази даних
echo ========================================================
echo.
echo Зараз потрібно створити базу даних.
echo Введіть пароль користувача postgres (який вказали при установці)
echo.

psql -U postgres -c "CREATE DATABASE law_crm_db;" 2>nul
psql -U postgres -c "CREATE USER law_crm_user WITH PASSWORD 'password123';" 2>nul
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE law_crm_db TO law_crm_user;" 2>nul

if errorlevel 1 (
    echo.
    echo [!] Не вдалося створити БД автоматично
    echo.
    echo Створіть базу вручну:
    echo 1. Відкрийте pgAdmin або виконайте: psql -U postgres
    echo 2. Виконайте:
    echo    CREATE DATABASE law_crm_db;
    echo    CREATE USER law_crm_user WITH PASSWORD 'password123';
    echo    GRANT ALL PRIVILEGES ON DATABASE law_crm_db TO law_crm_user;
    echo.
    set /p continue="База створена? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
) else (
    echo [OK] База даних створена!
)

echo.
echo ========================================================
echo КРОК 2: Налаштування Python оточення
echo ========================================================
echo.

REM Создание venv
if not exist venv (
    echo [i] Створення віртуального оточення...
    python -m venv venv
    if errorlevel 1 (
        echo [X] Помилка створення venv
        pause
        exit /b 1
    )
    echo [OK] Віртуальне оточення створено
) else (
    echo [OK] Віртуальне оточення вже існує
)
echo.

REM Активация venv
echo [i] Активація віртуального оточення...
call venv\Scripts\activate.bat

REM Fix for Windows encoding issues with PostgreSQL
set PYTHONUTF8=1
set APPDATA=%TEMP%
set PGPASSFILE=nul
set PGSERVICEFILE=nul
set PGSYSCONFDIR=nul
set PGCLIENTENCODING=UTF8

REM Обновление pip
echo [i] Оновлення pip...
python -m pip install --upgrade pip --quiet

REM Установка зависимостей
echo [i] Установка залежностей (це займе 2-5 хвилин)...
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo [X] Помилка установки залежностей
    pause
    exit /b 1
)

echo.
echo [OK] Залежності встановлено!
echo.

echo ========================================================
echo КРОК 3: Налаштування конфігурації
echo ========================================================
echo.

REM Создание .env
if not exist .env (
    echo [i] Створення .env файлу...
    copy .env.example .env >nul
    
    REM Генерация SECRET_KEY
    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" > temp_key.txt 2>nul
    if exist temp_key.txt (
        set /p SECRET_KEY=<temp_key.txt
        del temp_key.txt
    )
    
    echo [OK] .env файл створено
    echo.
    echo ВАЖЛИВО: Якщо ви використовували інший пароль для law_crm_user,
    echo відредагуйте файл .env та змініть DB_PASSWORD
) else (
    echo [OK] .env файл вже існує
)
echo.

echo ========================================================
echo КРОК 4: Ініціалізація бази даних
echo ========================================================
echo.

REM Миграции
echo [i] Створення таблиць в БД...
python manage.py migrate --noinput

if errorlevel 1 (
    echo.
    echo [X] Помилка міграції
    echo.
    echo Можливі причини:
    echo 1. Неправильний пароль в .env (DB_PASSWORD)
    echo 2. PostgreSQL не запущено
    echo 3. База даних не створена
    echo.
    echo Перевірте налаштування та спробуйте знову
    pause
    exit /b 1
)

echo [OK] Таблиці створено
echo.

REM Статика
echo [i] Збирання статичних файлів...
python manage.py collectstatic --noinput --clear >nul 2>&1
echo [OK] Статика зібрана
echo.

echo ========================================================
echo КРОК 5: Створення адміністратора
echo ========================================================
echo.
echo Зараз потрібно створити адміністратора системи.
echo Введіть дані:
echo.

python manage.py createsuperuser

if errorlevel 1 (
    echo [!] Не вдалося створити користувача
    pause
    exit /b 1
)

echo.
echo [OK] Адміністратора створено!
echo.

echo ========================================================
echo КРОК 6: Завантаження демо-даних (опціонально)
echo ========================================================
echo.
set /p load_demo="Завантажити тестові дані для демонстрації? (y/n): "

if /i "%load_demo%"=="y" (
    echo [i] Завантаження демо даних...
    python manage.py shell < scripts\create_demo_data.py
    echo.
    echo [OK] Демо дані завантажено!
    echo.
    echo Тестові користувачі:
    echo   Партнер:  partner / partner123
    echo   Адвокат:  lawyer1 / lawyer123
    echo   Помічник: assistant / assistant123
)

echo.
echo ========================================================
echo [OK] УСТАНОВКА ЗАВЕРШЕНА!
echo ========================================================
echo.
echo Система готова до роботи!
echo.
echo Для запуску сервера виконайте:
echo   1. venv\Scripts\activate
echo   2. python manage.py runserver
echo.
echo Або просто запустіть: run.bat
echo.
echo Після запуску відкрийте в браузері:
echo   http://localhost:8000
echo.
echo Панель адміністрування:
echo   http://localhost:8000/admin
echo.
pause

REM Спрашиваем, запустить ли сервер сейчас
echo.
set /p start_now="Запустити сервер зараз? (y/n): "

if /i "%start_now%"=="y" (
    echo.
    echo ========================================================
    echo Запуск сервера...
    echo ========================================================
    echo.
    echo Відкрийте в браузері: http://localhost:8000
    echo.
    echo Для зупинки натисніть Ctrl+C
    echo.
    python manage.py runserver
)

