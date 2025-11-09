@echo off
echo ========================================
echo   AIGolos - Starting Development Server
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Fix encoding for Windows
echo Fixing encoding...
python -c "import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')" 2>nul
chcp 65001 >nul 2>&1

REM Run migrations
echo Running migrations...
python manage.py migrate

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput

REM Start server
echo.
echo Starting Django development server...
echo Open http://127.0.0.1:8000 in your browser
echo Press Ctrl+C to stop the server
echo.
python manage.py runserver

