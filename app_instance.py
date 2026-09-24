"""One application per Windows user; a second launch opens the dashboard."""
import ctypes
import getpass
import hashlib
from PySide6.QtNetwork import QLocalServer, QLocalSocket

ERROR_ALREADY_EXISTS = 183
_instance_mutex = None


def acquire_instance():
    """Acquire single instance using Windows named mutex and IPC pipe."""
    global _instance_mutex
    user_hash = hashlib.sha256(getpass.getuser().encode()).hexdigest()[:16]
    mutex_name = f"Local\\DeskPetMutex-{user_hash}"
    pipe_name = f"DeskPet-{user_hash}"

    try:
        kernel32 = ctypes.windll.kernel32
        _instance_mutex = kernel32.CreateMutexW(None, True, mutex_name)
        last_error = kernel32.GetLastError()
    except Exception:
        # Fallback if ctypes fails
        last_error = 0

    if last_error == ERROR_ALREADY_EXISTS:
        # DeskPet is already running; send signal to show dashboard and exit
        probe = QLocalSocket()
        probe.connectToServer(pipe_name)
        if probe.waitForConnected(800):
            probe.write(b"show\n")
            probe.waitForBytesWritten(800)
            probe.disconnectFromServer()
        return None

    # First instance: clean up any dangling pipe and listen
    QLocalServer.removeServer(pipe_name)
    server = QLocalServer()
    if not server.listen(pipe_name):
        QLocalServer.removeServer(pipe_name)
        server.listen(pipe_name)
    return server
