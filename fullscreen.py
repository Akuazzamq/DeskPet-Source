"""Best-effort fullscreen detection using native monitor coordinates."""
import ctypes
import sys
from ctypes import wintypes


class FullscreenMonitor:
    def __init__(self):
        self.api = None
        if sys.platform != 'win32':
            return
        self.api = ctypes.WinDLL('user32', use_last_error=True)
        self.api.GetForegroundWindow.restype = wintypes.HWND
        self.api.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        self.api.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
        self.api.MonitorFromWindow.restype = wintypes.HANDLE
        self.api.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        self.api.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.c_void_p]

    def covers(self, pet_handle):
        if not self.api:
            return False
        foreground = self.api.GetForegroundWindow()
        if not foreground or foreground == pet_handle:
            return False
        name = ctypes.create_unicode_buffer(256)
        self.api.GetClassNameW(foreground, name, 256)
        if name.value in ('Progman', 'WorkerW', 'Shell_TrayWnd', 'Shell_SecondaryTrayWnd'):
            return False
        monitor = self.api.MonitorFromWindow(foreground, 2)
        if monitor != self.api.MonitorFromWindow(pet_handle, 2):
            return False
        class MONITORINFO(ctypes.Structure):
            _fields_ = [('cbSize', wintypes.DWORD), ('rcMonitor', wintypes.RECT),
                        ('rcWork', wintypes.RECT), ('dwFlags', wintypes.DWORD)]
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(info)
        rect = wintypes.RECT()
        if not self.api.GetMonitorInfoW(monitor, ctypes.byref(info)) or not self.api.GetWindowRect(foreground, ctypes.byref(rect)):
            return False
        # Exact bounds avoid treating maximized windows with resize borders as fullscreen.
        return all(abs(getattr(rect, edge) - getattr(info.rcMonitor, edge)) <= 1
                   for edge in ('left', 'top', 'right', 'bottom'))
