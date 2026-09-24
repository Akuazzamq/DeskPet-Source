import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_behavior import app
from main import DesktopPet
from dashboard import Dashboard
from PySide6.QtCore import QSettings

class DashboardTests(unittest.TestCase):
    def test_controls_and_close_keep_pet(self):
        with tempfile.TemporaryDirectory() as folder, patch('dashboard.startup.enabled',return_value=False):
            pet=DesktopPet(QSettings(folder+'/prefs.ini',QSettings.IniFormat));pet.timer.stop()
            dash=Dashboard(pet)
            try:
                dash.show();app.processEvents()
                dash.types.setCurrentIndex(dash.types.findData('duck'))
                dash.skins.setCurrentIndex(dash.skins.findData('azzamq_duck'))
                self.assertEqual(pet.pet.skin,'azzamq_duck')
                dash.mode.setCurrentIndex(dash.mode.findData('taskbar'))
                self.assertEqual(pet.mode,'taskbar')
                dash.wander.setChecked(False)
                self.assertFalse(pet.behavior.wander)
                dash.minutes.setValue(15);dash.start_timer()
                self.assertIsNotNone(pet.time_tools.deadline)
                self.assertEqual(pet.time_tools.mode,'timer')
                self.assertEqual(dash.time_display.text(),'00:15:00')
                dash.toggle_timer();self.assertIsNone(pet.time_tools.deadline)
                self.assertEqual(dash.timer_toggle.text(),'Resume')
                dash.toggle_timer();self.assertIsNotNone(pet.time_tools.deadline)
                dash.reset_timer();self.assertEqual(pet.time_tools.remaining,15*60)
                dash.time_mode.setCurrentIndex(dash.time_mode.findData('stopwatch'))
                dash.toggle_stopwatch();self.assertIsNotNone(pet.time_tools.started)
                dash.toggle_stopwatch();self.assertIsNone(pet.time_tools.started)
                dash.reset_stopwatch();self.assertEqual(pet.time_tools.elapsed,0)
                dash.time_mode.setCurrentIndex(dash.time_mode.findData('clock'))
                self.assertEqual(pet.time_tools.mode,'clock')
                dash.time_bar_style.setCurrentIndex(dash.time_bar_style.findData('comic'))
                self.assertEqual(pet.time_bar_style,'comic')
                self.assertEqual(pet.settings.value('time_bar_style'),'comic')
                dash.time_bar_style.setCurrentIndex(dash.time_bar_style.findData('wood'))
                self.assertEqual(pet.time_bar_style,'wood')
                dash.time_bar_style.setCurrentIndex(dash.time_bar_style.findData('cloud'))
                self.assertEqual(pet.time_bar_style,'cloud')
                dash.time_bar_style.setCurrentIndex(dash.time_bar_style.findData('arcade'))
                self.assertEqual(pet.time_bar_style,'arcade')
                dash.toggle_pause();self.assertTrue(pet.behavior.paused)
                Path('artifacts').mkdir(exist_ok=True)
                app.processEvents();dash.grab().save('artifacts/dashboard.png')
                dash.close();self.assertFalse(dash.isVisible())
                self.assertTrue(pet.isVisible())
            finally:
                dash.preview.timer.stop();dash.time_refresh.stop();dash.deleteLater()
                pet.close()
                if pet.tray:pet.tray.hide()
                app.aboutToQuit.disconnect(pet.save_settings)
                app.screenAdded.disconnect(pet.screen_changed)
                app.screenRemoved.disconnect(pet.screen_changed)

    def test_single_instance_activation(self):
        import uuid
        from app_instance import acquire_instance
        from PySide6.QtNetwork import QLocalServer
        with patch('app_instance.getpass.getuser',return_value='test-'+uuid.uuid4().hex):
            server=acquire_instance()
            self.assertIsNotNone(server)
            try:
                self.assertIsNone(acquire_instance())
                app.processEvents()
                self.assertTrue(server.hasPendingConnections())
                while server.hasPendingConnections():
                    connection=server.nextPendingConnection()
                    connection.close();connection.deleteLater()
            finally:
                name=server.serverName();server.close();QLocalServer.removeServer(name)

if __name__=='__main__':unittest.main()
