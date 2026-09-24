# Manual test: DeskPet beta

Use the newly built `dist/DeskPet-Setup.exe`, not the old DesktoPet package. Close the running source version from the pet's **Quit** menu before testing. If you previously installed DesktoPet, uninstall that beta first for a clean install test.

## 1. Normal installer

1. Double-click `dist/DeskPet-Setup.exe`.
2. Complete the wizard with **Create a desktop shortcut** checked.
3. Confirm DeskPet appears on the desktop, Start Menu and Windows Settings > Apps.
4. Open the shortcut: the dashboard and pet should appear without Python or a terminal.
5. Open the shortcut again: the existing dashboard should return, without another pet.

## 2. Dashboard and pet

- Switch animal and skin, including AzzamQ. The preview and actual pet should agree.
- Desktop mode: drag the pet; it should remain stationary after release.
- Taskbar mode: it should walk/run along the work-area edge. Wait 30-60 seconds for special actions.
- Click, drag and release; check responses and wall antics.
- Start a 1-minute timer and wait for completion.
- Pause/resume animations, disable walking, and verify both controls.
- Leave the PC untouched for 3 minutes: sleep, then wake with activity.
- Close the dashboard: the pet remains. Reopen via right-click > Open dashboard.
- Quit and reopen: animal, skin, mode and saved settings should persist.
- Optionally enable Launch with Windows, sign out/in, and verify only the pet opens. Disable it afterwards if unwanted.

## 3. Terminal installer

Uninstall DeskPet first if you want to test a fresh installation rather than an upgrade. In PowerShell, from the project folder:

```powershell
$hash = (Get-FileHash .\dist\DeskPet-Setup.exe -Algorithm SHA256).Hash
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -InstallerPath .\dist\DeskPet-Setup.exe -Sha256 $hash
```

Expected: DESKPET banner, checksum verification, installation, shortcuts and dashboard. Add `-CheckOnly` to verify the package without installing. The local hash checks the installation flow; release users receive the checksum manifest with the release assets.

The GitHub download path cannot be tested publicly until the repository and Release assets exist. Then use `-Repository OWNER/REPO`, plus `-Version v0.1.0-beta` for a prerelease tag.

## 4. Uninstall and clean PC

Uninstall through Windows Settings > Apps > DeskPet. Confirm the executable and shortcuts are removed. User preferences are intentionally retained.

For release confidence, repeat the setup and terminal tests on a Windows 10/11 x64 PC or VM without Python. Test 125%/150% display scaling and a second monitor if available. Record any problem with the steps, expected result, actual result and screenshot.

The beta installer is not digitally signed. No public download URL has been published yet.
