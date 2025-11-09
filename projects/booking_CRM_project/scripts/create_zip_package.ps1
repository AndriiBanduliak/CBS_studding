# Create ZIP package instead of .exe installer
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$Dist = Join-Path $Root 'dist_app'
$ZipOutput = Join-Path $Root 'RentMasterCRM.zip'

if (-not (Test-Path $Dist)) {
    Write-Error "dist_app not found. Run build_and_package.ps1 first."
    exit 1
}

Write-Host "==> Creating ZIP package..." -ForegroundColor Cyan

# Remove old ZIP if exists
if (Test-Path $ZipOutput) { Remove-Item $ZipOutput -Force }

# Create ZIP
Compress-Archive -Path "$Dist\*" -DestinationPath $ZipOutput -Force

Write-Host "==> ZIP package created: $ZipOutput" -ForegroundColor Green
Write-Host "==> User should extract this ZIP and run start_crm.bat" -ForegroundColor Yellow

