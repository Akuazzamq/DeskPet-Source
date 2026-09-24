param([string]$Compiler)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$env:PYINSTALLER_CONFIG_DIR = Join-Path $PSScriptRoot 'build\pyinstaller-cache'
& .\.venv\Scripts\python.exe packaging\make_icon.py
if ($LASTEXITCODE -ne 0) { throw 'Icon generation failed' }
& .\.venv\Scripts\python.exe -m unittest discover -q
if ($LASTEXITCODE -ne 0) { throw 'Tests failed; release artifacts were not rebuilt' }
& .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --windowed --onedir --icon assets\deskpet.ico --version-file packaging\version_info.txt --add-data "assets\deskpet.ico;assets" --add-data "assets\deskpet_title.png;assets" --name DeskPet main.py
if ($LASTEXITCODE -ne 0) { throw 'DeskPet build failed' }
Copy-Item -LiteralPath README.md -Destination dist\DeskPet\README.md
Copy-Item -LiteralPath LICENSE -Destination dist\DeskPet\LICENSE
$zip = Join-Path $PSScriptRoot 'dist\DeskPet-Windows.zip'
$zipBuilt = $false
for ($attempt = 1; $attempt -le 3 -and -not $zipBuilt; $attempt++) {
    try {
        Compress-Archive -Path dist\DeskPet -DestinationPath $zip -Force
        $zipBuilt = $true
    } catch {
        if ($attempt -eq 3) { throw }
        Start-Sleep -Milliseconds 750
    }
}
if (-not $Compiler) {
    $candidates = @((Join-Path $PSScriptRoot 'build\tools\inno\ISCC.exe'),
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe")
    $Compiler = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $Compiler) { throw 'Portable ZIP built. Install Inno Setup or pass -Compiler path\ISCC.exe to build Setup.' }
& $Compiler packaging\deskpet.iss
if ($LASTEXITCODE -ne 0) { throw 'Setup build failed' }
Copy-Item -LiteralPath install.ps1 -Destination dist\install.ps1
$lines = foreach ($name in @('DeskPet-Setup.exe','DeskPet-Windows.zip','install.ps1')) {
    $hash = (Get-FileHash -LiteralPath (Join-Path dist $name) -Algorithm SHA256).Hash.ToLowerInvariant()
    "$hash  $name"
}
$lines | Set-Content -Encoding ascii dist\SHA256SUMS.txt
foreach ($line in $lines) {
    if ($line -notmatch '^([a-f0-9]{64})\s+(.+)$') { throw 'Generated checksum manifest is invalid' }
    $actual = (Get-FileHash -LiteralPath (Join-Path dist $Matches[2]) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $Matches[1]) { throw "Checksum verification failed for $($Matches[2])" }
}
Write-Host 'Ready: Setup EXE, portable ZIP, terminal installer, SHA256SUMS.txt' -ForegroundColor Green
