import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import tempfile
import unittest
from pathlib import Path
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QImage, QPainter, QColor, QFont, QFontDatabase
from PySide6.QtWidgets import QApplication
from behavior import Behavior
from pet_engine import PetEngine
from main import DesktopPet

app = QApplication.instance() or QApplication([])
# Offscreen Qt may not discover Windows fonts automatically.
font_path = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts' / 'segoeui.ttf'
if font_path.exists():
    QFontDatabase.addApplicationFont(str(font_path))


class BehaviorTests(unittest.TestCase):
    def test_sleep_wake_all_pets(self):
        for skin in PetEngine().pets:
            pet = PetEngine()
            pet.set_skin(skin)
            b = Behavior(pet, 0)
            b.tick(180, 180)
            self.assertEqual(pet.state, 'drowsy')
            b.tick(183, 183)
            self.assertEqual(pet.state, 'sleeping')
            b.tick(184, 0)
            self.assertEqual(pet.state, 'stretch')
            b.tick(186, 0)
            self.assertNotIn(pet.state, ('drowsy', 'sleeping', 'stretch'))

    def test_blink_does_not_postpone_activity(self):
        b = Behavior(PetEngine(), 0)
        b.tick(3, 0)
        self.assertEqual(b.pet.state, 'blink')
        deadline = b.next_action
        b.tick(3.2, 0)
        self.assertEqual(b.next_action, deadline)
        b.tick(5, 0)
        self.assertIn(b.pet.state, ('walking', 'look', 'sniff', 'groom'))

    def test_natural_schedule_reaches_walking(self):
        for skin in PetEngine().pets:
            for seed in range(10):
                pet = PetEngine()
                pet.set_skin(skin)
                b = Behavior(pet, 0)
                b.taskbar = True
                b.rng.seed(seed)
                walked = False
                for step in range(800):
                    b.tick(step * .05, 0)
                    walked |= pet.state == 'walking'
                self.assertTrue(walked, (skin, seed))

    def test_sleep_visual_progress_and_pause(self):
        pet = PetEngine()
        b = Behavior(pet, 0)
        b.tick(180, 180)
        self.assertEqual(pet.sleep_progress, 0)
        b.tick(181.5, 181.5)
        self.assertAlmostEqual(pet.sleep_progress, .5)
        b.tick(183, 183)
        self.assertEqual(pet.state, 'sleeping')
        self.assertEqual(pet.sleep_progress, 1)
        phase = pet.breath_phase
        b.paused = True
        b.tick(184, 184)
        self.assertEqual(pet.breath_phase, phase)
        b.paused = False
        b.tick(185, 0)
        self.assertEqual(pet.state, 'stretch')

    def test_interruption_and_pause(self):
        b = Behavior(PetEngine(), 0)
        b.interact('held', 0)
        b.tick(200, 200)
        self.assertEqual(b.pet.state, 'held')
        b.interact('settle', .65)
        b.tick(201, 0)
        self.assertNotEqual(b.pet.state, 'held')
        b.paused = True
        state = b.pet.state
        b.tick(500, 500)
        self.assertEqual(b.pet.state, state)
        b.paused = False
        b.sleep_enabled = False
        b.tick(501, 501)
        self.assertNotIn(b.pet.state, ('sleeping', 'drowsy'))

    def test_widget_settings_and_render(self):
        with tempfile.TemporaryDirectory() as folder:
            settings = QSettings(str(Path(folder) / 'settings.ini'), QSettings.IniFormat)
            window = DesktopPet(settings)
            window.timer.stop()
            states = ['idle', 'curious', 'happy', 'drowsy', 'sleeping', 'stretch', 'held', 'groom', 'look', 'sniff', 'walking', 'settle']
            sheet = QImage(130 * len(states), 170 * len(window.pet.pets), QImage.Format_ARGB32)
            sheet.fill(QColor('#343744'))
            painter = QPainter(sheet)
            painter.setFont(QFont("Segoe UI", 10))
            for row, skin in enumerate(window.pet.pets):
                window.change_pet(skin)
                for col, state in enumerate(states):
                    window.pet.set_state(state)
                    window.pet.draw(painter, col * 130 + 8, row * 170 + 40)
                    painter.setPen(QColor('white'))
                    painter.drawText(col * 130 + 5, row * 170 + 18, state)
            painter.end()
            Path('artifacts').mkdir(exist_ok=True)
            self.assertTrue(sheet.save('artifacts/poses.png'))
            window.change_pet('black_cat')
            window.behavior.wander = False
            window.select_time_bar_style('comic')
            window.save_settings()
            other = DesktopPet(settings)
            self.assertEqual(other.pet.skin, 'black_cat')
            self.assertFalse(other.behavior.wander)
            self.assertEqual(other.time_bar_style, 'comic')
            # Every species signature must render safely on every time-bar model.
            bar_sheet = QImage(130 * 5, 50 * 10, QImage.Format_ARGB32)
            bar_sheet.fill(Qt.transparent)
            bar_painter = QPainter(bar_sheet)
            kinds = {}
            for skin, data in window.pet.pets.items():
                kinds.setdefault(data['type'], skin)
            for row, skin in enumerate(kinds.values()):
                window.change_pet(skin)
                window.current_time = '12:34'
                for col, style in enumerate(('pixel', 'comic', 'wood', 'cloud', 'arcade')):
                    window.time_bar_style = style
                    bar_painter.save(); bar_painter.translate(col * 130, row * 50)
                    window.draw_clock(bar_painter); bar_painter.restore()
            bar_painter.end()
            self.assertTrue(bar_sheet.save('artifacts/species-time-bars.png'))
            other.timer.stop()
            window.close()
            other.close()
            app.aboutToQuit.disconnect(window.save_settings)
            app.aboutToQuit.disconnect(other.save_settings)


if __name__ == '__main__':
    unittest.main()
