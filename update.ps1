[CmdletBinding()]
param([switch]$NoLaunch)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

Write-Host "=== Updating DeskPet ===" -ForegroundColor Magenta

# 1. Close any running DeskPet instance
Write-Host "[1/3] Closing running DeskPet..." -ForegroundColor Cyan
Get-Process -Name DeskPet -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Build release
Write-Host "[2/3] Compiling update..." -ForegroundColor Cyan
& powershell -NoProfile -ExecutionPolicy Bypass -File .\build.ps1
if ($LASTEXITCODE -ne 0) { throw "DeskPet build failed with exit code $LASTEXITCODE. The installed version was not changed." }

$setup = Join-Path $PSScriptRoot 'dist\DeskPet-Setup.exe'
if (-not (Test-Path -LiteralPath $setup)) { throw 'Build completed without producing dist\DeskPet-Setup.exe.' }

# 3. Install
Write-Host "[3/3] Installing latest update..." -ForegroundColor Cyan
$hash = (Get-FileHash -LiteralPath $setup -Algorithm SHA256).Hash
$installArgs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', '.\install.ps1', '-InstallerPath', $setup, '-Sha256', $hash)
if ($NoLaunch) { $installArgs += '-NoLaunch' }
& powershell @installArgs
if ($LASTEXITCODE -ne 0) { throw "DeskPet installation failed with exit code $LASTEXITCODE." }

Write-Host "DeskPet successfully updated!" -ForegroundColor Green
