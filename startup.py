"""Optional Windows login startup; only changed from the user's menu action."""
import subprocess
import sys
from pathlib import Path

RUN_KEY = r'Software\Microsoft\Windows\CurrentVersion\Run'


def enabled():
    if sys.platform != 'win32':
        return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.QueryValueEx(key, 'DeskPet')
        return True
    except FileNotFoundError:
        return False


def set_enabled(value):
    import winreg
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        if value:
            if getattr(sys, 'frozen', False):
                command = subprocess.list2cmdline([sys.executable, '--background'])
            else:
                executable = Path(sys.executable).with_name('pythonw.exe')
                if not executable.exists():
                    executable = Path(sys.executable)
                command = subprocess.list2cmdline([str(executable), str(Path(__file__).with_name('main.py').resolve()), '--background'])
            winreg.SetValueEx(key, 'DeskPet', 0, winreg.REG_SZ, command)
        else:
            try:
                winreg.DeleteValue(key, 'DeskPet')
            except FileNotFoundError:
                pass
