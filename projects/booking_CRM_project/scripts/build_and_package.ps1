Param(
    [string]$PythonExe = "python",
    [string]$NodeExe = "npm"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Paths
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$Frontend = Join-Path $Root 'frontend'
$Dist = Join-Path $Root 'dist_app'
$AppDir = Join-Path $Dist 'app'
$TemplatesDir = Join-Path $AppDir 'templates'
$VenvDir = Join-Path $Dist 'venv'

Write-Host "==> Clean previous dist" -ForegroundColor Cyan
if (Test-Path $Dist) { Remove-Item $Dist -Recurse -Force }
New-Item -ItemType Directory -Path $Dist | Out-Null
New-Item -ItemType Directory -Path $AppDir | Out-Null

Write-Host "==> Build frontend" -ForegroundColor Cyan
Push-Location $Frontend

# Clean node_modules if exists to avoid EBUSY errors on Windows
$NodeModulesPath = Join-Path $Frontend 'node_modules'
if (Test-Path $NodeModulesPath) {
    Write-Host "Cleaning existing node_modules..." -ForegroundColor Yellow
    try {
        Remove-Item -Path $NodeModulesPath -Recurse -Force -ErrorAction Stop
    } catch {
        Write-Warning "Could not remove node_modules (may be locked): $($_.Exception.Message)"
        Write-Warning "Please close all programs using node_modules and try again"
        throw "node_modules is locked. Close IDE/terminals and retry."
    }
}

# More robust install on Windows to avoid EBUSY on node_modules
$installed = $false
for ($i=1; $i -le 3; $i++) {
    try {
        & $NodeExe install --no-audit --no-fund --include=dev
        $installed = $true
        break
    } catch {
        Write-Warning "npm install attempt $i failed: $($_.Exception.Message)"
        if ($i -lt 3) { Start-Sleep -Seconds (2 * $i) }
    }
}
if (-not $installed) { throw "npm install failed after 3 attempts" }

# Prefer npx to ensure vite is available even if local install has issues
$viteBuilt = $false
try {
    npx vite build
    $viteBuilt = $true
} catch {
    Write-Warning "Local npx vite build failed, trying temporary vite install..."
}
if (-not $viteBuilt) {
    try {
        npx --yes vite@7 build
        $viteBuilt = $true
    } catch {
        Write-Error "Vite build failed: $($_.Exception.Message)"
        throw
    }
}
Pop-Location

$FrontDist = Join-Path $Frontend 'dist'
if (-not (Test-Path $FrontDist)) { throw "Frontend dist not found: $FrontDist" }

Write-Host "==> Prepare templates and static assets" -ForegroundColor Cyan
New-Item -ItemType Directory -Path $TemplatesDir -Force | Out-Null

# Copy and rewrite index.html to use /static/assets/
$indexPath = Join-Path $FrontDist 'index.html'
$indexContent = Get-Content $indexPath -Raw
$indexContent = $indexContent -replace '"/assets/', '"/static/assets/'
Set-Content -Path (Join-Path $TemplatesDir 'index.html') -Value $indexContent -Encoding UTF8

# Copy assets to staticfiles/assets (we will copy staticfiles later)
$StaticRoot = Join-Path $Root 'staticfiles'
if (Test-Path $StaticRoot) { Remove-Item $StaticRoot -Recurse -Force }
New-Item -ItemType Directory -Path (Join-Path $StaticRoot 'assets') -Force | Out-Null
Copy-Item -Recurse -Force (Join-Path $FrontDist 'assets') (Join-Path $StaticRoot 'assets')

Write-Host "==> Copy backend application files" -ForegroundColor Cyan
$BackendItems = @(
    'manage.py',
    'rentmaster',
    'accounts','audit','bookings','customers','integrations','notes','properties','rates','reports','staff','tasks'
)
foreach ($item in $BackendItems) {
    $src = Join-Path $Root $item
    if (Test-Path $src) {
        Copy-Item -Recurse -Force $src $AppDir
    }
}

# Copy runtime files
Copy-Item (Join-Path $Root 'requirements.txt') $Dist -Force
if (Test-Path (Join-Path $Root 'db.sqlite3')) {
    Copy-Item (Join-Path $Root 'db.sqlite3') $Dist -Force
}

Write-Host "==> Create virtual environment and install dependencies" -ForegroundColor Cyan
& $PythonExe -m venv $VenvDir
$Pip = Join-Path $VenvDir 'Scripts\pip.exe'
$Py = Join-Path $VenvDir 'Scripts\python.exe'
& $Pip install --upgrade pip
& $Pip install -r (Join-Path $Dist 'requirements.txt')
# Ensure whitenoise is present for static serving
& $Pip install whitenoise

Write-Host "==> Collect static files" -ForegroundColor Cyan
Push-Location $AppDir
$env:DJANGO_SETTINGS_MODULE = 'rentmaster.settings'
# Create minimal .env for production runtime
@(
    'DEBUG=false',
    'ALLOWED_HOSTS=127.0.0.1,localhost',
    'CORS_ALLOW_ALL_ORIGINS=false'
) | Set-Content -Path (Join-Path $AppDir '.env') -Encoding UTF8

& $Py manage.py collectstatic --noinput
& $Py manage.py migrate --noinput
Pop-Location

# Copy frontend assets into collected static (after collectstatic to ensure they're available)
# IMPORTANT: Must copy AFTER collectstatic, and ensure no nested assets folder
$AssetsSource = Join-Path $Frontend 'dist\assets'
$AssetsDest = Join-Path $AppDir 'staticfiles\assets'
if (Test-Path $AssetsDest) { 
    Remove-Item $AssetsDest -Recurse -Force 
    Write-Host "Removed existing assets folder" -ForegroundColor Yellow
}
New-Item -ItemType Directory -Path $AssetsDest -Force | Out-Null
# Copy files directly, not the folder itself
Get-ChildItem $AssetsSource -File | ForEach-Object {
    Copy-Item $_.FullName $AssetsDest -Force
    Write-Host "Copied: $($_.Name)" -ForegroundColor Gray
}
Write-Host "Copied $(@(Get-ChildItem $AssetsDest -File).Count) asset files" -ForegroundColor Green

Write-Host "==> Create start script" -ForegroundColor Cyan
$StartBat = @'
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
'@
Set-Content -Path (Join-Path $Dist 'start_crm.bat') -Value $StartBat -Encoding ASCII

Write-Host "==> Done. Distribution at $Dist" -ForegroundColor Green

