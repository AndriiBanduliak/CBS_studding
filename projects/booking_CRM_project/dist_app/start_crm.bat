@echo off
setlocal enabledelayedexpansion
REM Get the directory where this batch file is located (with trailing backslash removed)
set "INSTALL_DIR=%~dp0"
set "INSTALL_DIR=%INSTALL_DIR:~0,-1%"
set "APP_DIR=%INSTALL_DIR%\app"
set "VENV=%INSTALL_DIR%\venv"
set "PY=%VENV%\Scripts\python.exe"

echo Install directory: %INSTALL_DIR%
echo App directory: %APP_DIR%
echo Python: %PY%

REM Check if Python exists
if not exist "%PY%" (
    echo.
    echo ERROR: Python not found at:
    echo %PY%
    echo.
    echo Please check the installation directory:
    echo %INSTALL_DIR%
    echo.
    pause
    exit /b 1
)

REM Check if app directory exists
if not exist "%APP_DIR%" (
    echo.
    echo ERROR: App directory not found:
    echo %APP_DIR%
    echo.
    pause
    exit /b 1
)

REM Change to app directory
cd /d "%APP_DIR%"
if errorlevel 1 (
    echo.
    echo ERROR: Cannot change to directory:
    echo %APP_DIR%
    echo.
    pause
    exit /b 1
)

echo.
echo Applying database migrations...
"%PY%" manage.py migrate --noinput
if errorlevel 1 (
    echo.
    echo ERROR: Failed to apply migrations!
    echo.
    pause
    exit /b 1
)

echo.
echo Starting RentMaster CRM server...
start "RentMaster CRM" "%PY%" manage.py runserver 0.0.0.0:8000 --nostatic
timeout /t 2 >nul
start "" http://localhost:8000/
endlocal
