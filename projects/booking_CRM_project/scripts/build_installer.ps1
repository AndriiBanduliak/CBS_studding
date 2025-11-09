# Build installer using Inno Setup
# Automatically finds ISCC.exe or offers alternatives

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$InstallerScript = Join-Path $Root 'scripts\installer.iss'
$Dist = Join-Path $Root 'dist_app'

# Check if dist_app exists
if (-not (Test-Path $Dist)) {
    Write-Error "dist_app not found. Run build_and_package.ps1 first."
    exit 1
}

# Find ISCC.exe
$PossiblePaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    "C:\Program Files\Inno Setup 5\ISCC.exe"
)

$ISCC = $null
foreach ($path in $PossiblePaths) {
    if (Test-Path $path) {
        $ISCC = $path
        break
    }
}

# Also try to find in registry or PATH
if (-not $ISCC) {
    $found = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($found) {
        $ISCC = $found.Source
    }
}

if (-not $ISCC) {
    Write-Host "==> Inno Setup not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "1. Install Inno Setup from: https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
    Write-Host "2. Use ZIP package instead:" -ForegroundColor Cyan
    Write-Host "   powershell -ExecutionPolicy Bypass -File .\scripts\create_zip_package.ps1" -ForegroundColor White
    Write-Host "3. Open installer.iss manually in Inno Setup GUI" -ForegroundColor Cyan
    exit 1
}

Write-Host "==> Found Inno Setup: $ISCC" -ForegroundColor Green
Write-Host "==> Building installer..." -ForegroundColor Cyan

# Create installer directory
$InstallerDir = Join-Path $Root 'installer'
if (-not (Test-Path $InstallerDir)) {
    New-Item -ItemType Directory -Path $InstallerDir | Out-Null
}

# Run ISCC
& $ISCC $InstallerScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "==> Installer created successfully!" -ForegroundColor Green
    Write-Host "==> Location: $InstallerDir\RentMasterCRMSetup.exe" -ForegroundColor Green
} else {
    Write-Error "Installer build failed with exit code $LASTEXITCODE"
    exit 1
}

