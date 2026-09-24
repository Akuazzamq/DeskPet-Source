[CmdletBinding()]
param(
    [string]$OutputDir = ""
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

if (-not $OutputDir) {
    $OutputDir = Join-Path $PSScriptRoot 'release_bundle'
}

Write-Host "=========================================" -ForegroundColor Magenta
Write-Host "   DeskPet Public Release Bundler       " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Magenta

# 1. Clean output directory
if (Test-Path -LiteralPath $OutputDir) {
    Remove-Item -LiteralPath $OutputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Path "$OutputDir\artifacts" | Out-Null
New-Item -ItemType Directory -Path "$OutputDir\assets" | Out-Null
New-Item -ItemType Directory -Path "$OutputDir\binaries" | Out-Null

# 2. Copy documentation and installer scripts
Copy-Item -LiteralPath "README.md" -Destination "$OutputDir\README.md"
Copy-Item -LiteralPath "LICENSE" -Destination "$OutputDir\LICENSE"
Copy-Item -LiteralPath "install.ps1" -Destination "$OutputDir\install.ps1"

# 3. Copy visual assets used by README
Copy-Item -Path "artifacts\*.png" -Destination "$OutputDir\artifacts" -Force
Copy-Item -Path "assets\*.png" -Destination "$OutputDir\assets" -Force
Copy-Item -Path "assets\*.ico" -Destination "$OutputDir\assets" -Force

# 4. Copy compiled release binaries (for GitHub Releases)
if (Test-Path -LiteralPath "dist\DeskPet-Setup.exe") {
    Copy-Item -LiteralPath "dist\DeskPet-Setup.exe" -Destination "$OutputDir\binaries\DeskPet-Setup.exe"
    Copy-Item -LiteralPath "dist\DeskPet-Windows.zip" -Destination "$OutputDir\binaries\DeskPet-Windows.zip"
    Copy-Item -LiteralPath "dist\install.ps1" -Destination "$OutputDir\binaries\install.ps1"
    Copy-Item -LiteralPath "dist\SHA256SUMS.txt" -Destination "$OutputDir\binaries\SHA256SUMS.txt"
}

# Clean any accidentally created root directory
if (Test-Path -LiteralPath "C:\release_bundle") {
    Remove-Item -LiteralPath "C:\release_bundle" -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "`nRelease bundle ready at: $OutputDir" -ForegroundColor Green
Write-Host "`nReady for GitHub distribution (0 Python files, 100% Freeware App bundle)." -ForegroundColor Cyan

