@echo off
chcp 65001 >nul
REM Запуск Django сервера с исправлением кодировки

echo ========================================================
echo          Law CRM - Запуск сервера
echo ========================================================
echo.

REM Проверка виртуального окружения
if not exist venv (
    echo [X] Виртуальное окружение не найдено!
    echo Выполните: install_local.bat
    pause
    exit /b 1
)

REM Установка всех необходимых переменных окружения
REM Эти переменные предотвращают чтение конфигурационных файлов с кириллическими путями
set PYTHONUTF8=1
set APPDATA=%TEMP%
set PGPASSFILE=nul
set PGSERVICEFILE=nul
set PGSYSCONFDIR=nul
set PGCLIENTENCODING=UTF8

echo [i] Запуск Django сервера...
echo.
echo Web-интерфейс: http://127.0.0.1:8000
echo Админ-панель:  http://127.0.0.1:8000/admin
echo.
echo Для остановки нажмите Ctrl+C
echo.

REM Запуск через простой WSGI сервер (без проверки миграций)
venv\Scripts\python.exe -X utf8=1 simple_server.py

