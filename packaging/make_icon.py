"""Export the approved D logo for Windows packaging, preserving transparency."""
from pathlib import Path
from PySide6.QtGui import QImage
from PySide6.QtCore import Qt
root = Path(__file__).resolve().parents[1]
image = QImage(str(root / 'assets/deskpet-logo-d.png'))
if image.isNull():
    raise RuntimeError('Approved DeskPet D logo is missing')
icon = image.scaled(256, 256, Qt.KeepAspectRatio, Qt.FastTransformation)
for name in ('deskpet.ico', 'deskpet.png'):
    if not icon.save(str(root / 'assets' / name)):
        raise RuntimeError('Could not export ' + name)
