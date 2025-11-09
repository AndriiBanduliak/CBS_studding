@echo off
REM Setup script for Law CRM (Windows version)
REM Автоматизация настройки и запуска системы

echo ========================================================
echo          Law CRM - Setup and Installation
echo     CRM для Адвокатського Об'єднання
echo ========================================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python не встановлено. Встановіть Python 3.10+
    pause
    exit /b 1
)
echo [OK] Python встановлено

REM Проверка Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [!] Docker не встановлено
    set DOCKER_AVAILABLE=0
) else (
    echo [OK] Docker встановлено
    set DOCKER_AVAILABLE=1
)

echo.
echo Виберіть режим установки:
echo 1) Docker (рекомендовано)
echo 2) Локальна установка
echo 3) Вихід
echo.
set /p choice="Ваш вибір: "

if "%choice%"=="1" goto docker_setup
if "%choice%"=="2" goto local_setup
if "%choice%"=="3" exit /b 0
echo Невірний вибір
goto :eof

:docker_setup
echo.
echo ========== Docker Installation ==========
echo.

if %DOCKER_AVAILABLE%==0 (
    echo [X] Docker не встановлено!
    pause
    exit /b 1
)

REM Створення .env файлу
if not exist .env (
    echo [i] Створення .env файлу...
    copy .env.example .env
    echo [OK] .env файл створено
)

REM Запуск Docker Compose
echo [i] Запуск Docker Compose...
docker-compose up -d --build

echo [i] Очікування запуску БД...
timeout /t 10 /nobreak >nul

REM Міграції
echo [i] Виконання міграцій...
docker-compose exec -T web python manage.py migrate

REM Суперпользователь
echo.
echo [i] Створення суперкористувача...
docker-compose exec web python manage.py createsuperuser

REM Статика
echo [i] Збирання статики...
docker-compose exec -T web python manage.py collectstatic --noinput

REM Демо данные
echo.
set /p load_demo="Завантажити демонстраційні дані? (y/n): "
if /i "%load_demo%"=="y" (
    echo [i] Завантаження демо даних...
    docker-compose exec -T web python manage.py shell < scripts\create_demo_data.py
)

echo.
echo ========================================================
echo [OK] Установка завершена!
echo ========================================================
echo.
echo Система доступна за адресою:
echo   http://localhost:8000
echo.
echo Панель адміністрування:
echo   http://localhost:8000/admin
echo.
echo Для зупинки: docker-compose down
echo.
pause
exit /b 0

:local_setup
echo.
echo ========== Локальна установка ==========
echo.

REM Створення віртуального оточення
if not exist venv (
    echo [i] Створення віртуального оточення...
    python -m venv venv
    echo [OK] Віртуальне оточення створено
)

REM Активація venv
call venv\Scripts\activate.bat

REM Установка залежностей
echo [i] Установка залежностей...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM .env файл
if not exist .env (
    echo [i] Створення .env файлу...
    copy .env.example .env
    echo [OK] .env файл створено
    echo [!] Відредагуйте .env файл та налаштуйте PostgreSQL
)

echo.
echo [!] ВАЖЛИВО: Переконайтеся що PostgreSQL встановлено та створено базу:
echo   CREATE DATABASE law_crm_db;
echo   CREATE USER law_crm_user WITH PASSWORD 'password';
echo   GRANT ALL PRIVILEGES ON DATABASE law_crm_db TO law_crm_user;
echo.
pause

REM Міграції
echo [i] Виконання міграцій...
python manage.py migrate

REM Суперпользователь
echo [i] Створення суперкористувача...
python manage.py createsuperuser

REM Статика
echo [i] Збирання статики...
python manage.py collectstatic --noinput

echo.
echo ========================================================
echo [OK] Локальна установка завершена!
echo ========================================================
echo.
echo Для запуску сервера:
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo Для запуску Celery (в окремих вікнах):
echo   celery -A law_crm worker -l info
echo   celery -A law_crm beat -l info
echo.
pause
exit /b 0

