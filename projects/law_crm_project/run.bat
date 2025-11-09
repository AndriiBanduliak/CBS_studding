@echo off
REM Швидкий запуск Law CRM

echo ========================================================
echo          Law CRM - Швидкий запуск
echo ========================================================
echo.

REM Проверка Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [i] Docker не знайдено, використовується локальний запуск...
    goto local_run
)

REM Проверка, запущен ли Docker Compose
docker-compose ps >nul 2>&1
if errorlevel 1 (
    echo [i] Запуск Docker Compose...
    docker-compose up -d
    timeout /t 5 /nobreak >nul
) else (
    echo [OK] Docker контейнери вже запущено
)

echo.
echo [OK] Система запущена!
echo.
echo Web-інтерфейс: http://localhost:8000
echo Адмін-панель:  http://localhost:8000/admin
echo.
echo Логи: docker-compose logs -f web
echo Зупинка: docker-compose down
echo.
pause
exit /b 0

:local_run
if not exist venv (
    echo [X] Віртуальне оточення не знайдено!
    echo Виконайте: setup.bat
    pause
    exit /b 1
)

echo [i] Активація віртуального оточення...
call venv\Scripts\activate.bat

REM Fix for Windows encoding issues with PostgreSQL
REM These variables prevent psycopg2 from reading config files with non-ASCII paths
set PYTHONUTF8=1
set APPDATA=%TEMP%
set PGPASSFILE=nul
set PGSERVICEFILE=nul
set PGSYSCONFDIR=nul
set PGCLIENTENCODING=UTF8

echo [i] Запуск Django сервера...
echo.
echo Web-інтерфейс: http://127.0.0.1:8000
echo.
python -X utf8=1 simple_server.py

