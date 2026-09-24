from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter

_icon_cache = {}


def application_icon():
    # PyInstaller places bundled data beside this module under _internal.
    return QIcon(str(Path(__file__).resolve().parent / 'assets' / 'deskpet.ico'))


def get_skin_icon(skin_key, size=28):
    cache_key = (skin_key, size)
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]
    from pet_engine import PetEngine
    engine = PetEngine()
    if skin_key not in engine.pets:
        return QIcon()
    engine.set_skin(skin_key)
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    scale = size / 114.0
    p.save()
    p.translate((size - 114 * scale) / 2, (size - 100 * scale) / 2 + 1)
    p.scale(scale, scale)
    engine.draw(p, 0, 0)
    p.restore()
    p.end()
    icon = QIcon(pix)
    _icon_cache[cache_key] = icon
    return icon


def get_type_icon(type_name, size=28):
    from pet_engine import PetEngine
    engine = PetEngine()
    skin = next((k for k, v in engine.pets.items() if v['type'] == type_name), None)
    if skin:
        return get_skin_icon(skin, size)
    return QIcon()
