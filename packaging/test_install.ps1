$ErrorActionPreference='Stop'
$workspace=(Resolve-Path $PSScriptRoot\..).Path
$target=Join-Path $workspace 'build\install-smoke'
if (-not [IO.Path]::GetFullPath($target).StartsWith($workspace + '\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Test target outside workspace' }
$key='HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{B1F3654D-65A4-43EF-B2DB-61B7B1337A19}_is1'
if (Test-Path -LiteralPath $key) { throw 'Existing DeskPet installation found; refusing to replace it during test.' }
if (Test-Path -LiteralPath $target) { throw 'Smoke-test folder already exists.' }
$setup=Join-Path $workspace 'dist\DeskPet-Setup.exe'
$log=Join-Path $workspace 'build\install-smoke.log'
$argsList=@('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-','/NOICONS','/TASKS=""',('/DIR="'+$target+'"'),('/LOG="'+$log+'"'))
$result=Start-Process -FilePath $setup -ArgumentList $argsList -WindowStyle Hidden -Wait -PassThru
if ($result.ExitCode -ne 0) { throw "Setup failed: $($result.ExitCode), log: $log" }
try {
    if (-not (Test-Path -LiteralPath (Join-Path $target 'DeskPet.exe'))) { throw 'Installed executable missing' }
    if (-not (Test-Path -LiteralPath (Join-Path $target '_internal\PySide6\Qt6Widgets.dll'))) { throw 'Bundled runtime missing' }
    $entry=Get-ItemProperty -LiteralPath $key
    if ($entry.InstallLocation.TrimEnd('\') -ne $target) { throw 'Unexpected install registration' }
    Write-Output 'PASS: setup installed executable, runtime and uninstall registration.'
} finally {
    $uninstaller=Join-Path $target 'unins000.exe'
    if (Test-Path -LiteralPath $uninstaller) {
        $result=Start-Process -FilePath $uninstaller -ArgumentList '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART' -WindowStyle Hidden -Wait -PassThru
        if ($result.ExitCode -ne 0) { throw "Uninstall failed: $($result.ExitCode)" }
    }
}
if (Test-Path -LiteralPath $key) { throw 'Uninstall registration remains' }
if (Test-Path -LiteralPath (Join-Path $target 'DeskPet.exe')) { throw 'Installed executable remains' }
Write-Output 'PASS: uninstall removed app and registration. No shortcuts were created during this test.'
