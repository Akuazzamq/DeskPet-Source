import ctypes
import sys
import time
from ctypes import wintypes


class IdleMonitor:
    """Read only the last-input timestamp, never key contents."""
    def __init__(self):
        self.last_local = time.monotonic()
        self.info_type = None
        if sys.platform == 'win32':
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [('cbSize', wintypes.UINT), ('dwTime', wintypes.DWORD)]
            self.info_type = LASTINPUTINFO
            self.user32 = ctypes.WinDLL('user32', use_last_error=True)
            self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            self.user32.GetLastInputInfo.argtypes = [ctypes.POINTER(LASTINPUTINFO)]
            self.user32.GetLastInputInfo.restype = wintypes.BOOL
            self.kernel32.GetTickCount.restype = wintypes.DWORD

    def activity(self):
        self.last_local = time.monotonic()

    def seconds(self):
        if self.info_type:
            info = self.info_type()
            info.cbSize = ctypes.sizeof(info)
            if self.user32.GetLastInputInfo(ctypes.byref(info)):
                return ((self.kernel32.GetTickCount() - info.dwTime) & 0xffffffff) / 1000
        return time.monotonic() - self.last_local
