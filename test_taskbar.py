import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtCore import QRect, QSettings, QPoint, Qt
from PySide6.QtTest import QTest
from test_behavior import app
from main import DesktopPet
from taskbar_motion import TaskbarMotion, floor_y


class TaskbarTests(unittest.TestCase):
    def test_destination_bounds_and_deceleration(self):
        for fox in (False, True):
            motion = TaskbarMotion()
            motion.rng.seed(2)
            x = -600
            speeds = []
            for _ in range(1200):
                x, direction, arrived = motion.step(x, -1000, -130, .05, fox)
                self.assertTrue(-1000 <= x <= -130)
                speeds.append(motion.speed)
                if arrived:
                    break
            self.assertTrue(arrived)
            self.assertLess(speeds[0], max(speeds))
            self.assertLess(speeds[-1], max(speeds))
            self.assertEqual(floor_y(QRect(-1920, 0, 1920, 1040)), 906)

    def test_modes_drag_pause_and_persistence(self):
        with tempfile.TemporaryDirectory() as folder:
            settings = QSettings(folder + '/test.ini', QSettings.IniFormat)
            w = DesktopPet(settings)
            w.timer.stop()
            w.hide_fullscreen = False
            w.show()
            w.set_mode('taskbar')
            w.constrain_taskbar()
            w.returning = False
            self.assertEqual(w.y() + 134, w.taskbar_screen().availableGeometry().bottom() + 1)
            QTest.mousePress(w, Qt.LeftButton, pos=QPoint(55,80))
            QTest.mouseMove(w, QPoint(85,40), 20)
            self.assertTrue(w.dragging)
            QTest.mouseRelease(w, Qt.LeftButton, pos=QPoint(85,40))
            self.assertTrue(w.returning)
            for _ in range(100):
                w.last_tick -= .05
                w.update_behavior()
            self.assertFalse(w.returning)
            w.behavior.enter('walking', 10)
            w.toggle_pause(True)
            old = w.pos()
            w.update_behavior()
            self.assertEqual(w.pos(), old)
            w.save_settings()
            other = DesktopPet(settings)
            other.timer.stop()
            self.assertEqual(other.mode, 'taskbar')
            w.set_mode('desktop')
            self.assertFalse(w.returning)
            for pet in (w, other):
                pet.close()
                if pet.tray:
                    pet.tray.hide()
                app.aboutToQuit.disconnect(pet.save_settings)
                app.screenRemoved.disconnect(pet.screen_changed)
                app.screenAdded.disconnect(pet.screen_changed)

    def test_taskbar_moves_without_forcing_walking(self):
        with tempfile.TemporaryDirectory() as folder:
            w = DesktopPet(QSettings(folder + '/natural.ini', QSettings.IniFormat))
            w.timer.stop()
            w.hide_fullscreen = False
            base = w.last_tick
            for skin in w.pet.pets:
                w.change_pet(skin)
                w.set_mode('desktop')
                with patch('main.time.monotonic', return_value=base):
                    w.set_mode('taskbar')
                w.constrain_taskbar()
                w.returning = False
                w.behavior.rng.seed(4)
                start = w.pos()
                moved = False
                with patch.object(w.idle, 'seconds', return_value=0):
                    for step in range(1, 400):
                        with patch('main.time.monotonic', return_value=base + step * .05):
                            w.update_behavior()
                        moved |= w.x() != start.x()
                self.assertTrue(moved, skin)
                base += 20
            w.close()
            if w.tray:
                w.tray.hide()
            app.aboutToQuit.disconnect(w.save_settings)
            app.screenRemoved.disconnect(w.screen_changed)
            app.screenAdded.disconnect(w.screen_changed)

    def test_taskbar_spends_most_time_moving(self):
        with tempfile.TemporaryDirectory() as folder:
            w = DesktopPet(QSettings(folder + '/active.ini', QSettings.IniFormat))
            w.timer.stop()
            w.hide_fullscreen = False
            base = w.last_tick
            for skin in w.pet.pets:
                w.change_pet(skin)
                w.set_mode('desktop')
                with patch('main.time.monotonic', return_value=base):
                    w.set_mode('taskbar')
                w.constrain_taskbar()
                w.returning = False
                w.behavior.rng.seed(5)
                w.motion.rng.seed(5)
                w.behavior.specials.rng.seed(5)
                moving = 0
                special = 0
                with patch.object(w.idle, 'seconds', return_value=0):
                    for step in range(1, 2401):
                        previous_x = w.x()
                        with patch('main.time.monotonic', return_value=base + step * .05):
                            w.update_behavior()
                        moving += w.x() != previous_x
                        special += w.pet.state == 'special'
                ratio = moving / 2400
                # Stationary species antics are intentional active time now.
                self.assertGreater(ratio, .45, (skin, ratio))
                self.assertGreater((moving + special) / 2400, .55, skin)
                self.assertLess(special / 2400, .18, skin)
                self.assertLess(ratio, .95, (skin, ratio))
                print(f'{skin}: {ratio:.0%} moving over simulated 120 seconds')
                base += 120
            w.close()
            if w.tray:
                w.tray.hide()
            app.aboutToQuit.disconnect(w.save_settings)
            app.screenRemoved.disconnect(w.screen_changed)
            app.screenAdded.disconnect(w.screen_changed)

    def test_wall_arrival_lift_and_click_cancel(self):
        with tempfile.TemporaryDirectory() as folder:
            w = DesktopPet(QSettings(folder + '/wall.ini', QSettings.IniFormat))
            w.timer.stop()
            w.hide_fullscreen = False
            w.set_mode('taskbar')
            w.returning = False
            area = w.taskbar_screen().availableGeometry()
            right = area.right() - w.width() + 1
            w.move(right, floor_y(area))
            base = w.last_tick
            w.behavior.next_climb = 0
            w.behavior.enter('walking', 10)
            w.motion.target = w.motion.x = float(right)
            with patch.object(w.idle, 'seconds', return_value=0):
                with patch('main.time.monotonic', return_value=base + .05):
                    w.update_behavior()
                self.assertEqual(w.pet.state, 'wall_look')
                for step in range(2, 26):
                    with patch('main.time.monotonic', return_value=base + step * .05):
                        w.update_behavior()
                self.assertEqual(w.pet.state, 'climbing')
                self.assertLess(w.y(), floor_y(area))
                self.assertEqual(w.y(), floor_y(area) - w.pet.wall_height)
                w.happy()
                w.update_behavior()
                self.assertEqual(w.pet.state, 'happy')
                self.assertEqual(w.y(), floor_y(area))
            w.close()
            if w.tray:
                w.tray.hide()
            app.aboutToQuit.disconnect(w.save_settings)
            app.screenRemoved.disconnect(w.screen_changed)
            app.screenAdded.disconnect(w.screen_changed)

    def test_fullscreen_restore(self):
        with tempfile.TemporaryDirectory() as folder:
            w = DesktopPet(QSettings(folder+'/test.ini', QSettings.IniFormat))
            w.timer.stop()
            w.show()
            with patch.object(w.fullscreen, 'covers', return_value=True):
                w.update_behavior()
                self.assertTrue(w.hidden_for_fullscreen)
                self.assertFalse(w.isVisible())
            with patch.object(w.fullscreen, 'covers', return_value=False):
                w.fullscreen_check = 0
                w.update_behavior()
                self.assertTrue(w.isVisible())
            w.close()
            if w.tray:
                w.tray.hide()
            app.aboutToQuit.disconnect(w.save_settings)
            app.screenRemoved.disconnect(w.screen_changed)
            app.screenAdded.disconnect(w.screen_changed)

if __name__ == '__main__':
    unittest.main()
