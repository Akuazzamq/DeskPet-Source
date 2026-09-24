import tempfile
import unittest
from pathlib import Path
from test_behavior import app
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QImage, QPainter, QColor, QFont
from PySide6.QtWidgets import QMenu
from pet_engine import PetEngine
from main import DesktopPet


class PenguinTests(unittest.TestCase):
    def test_menu_and_skin_memory(self):
        with tempfile.TemporaryDirectory() as folder:
            w=DesktopPet(QSettings(folder+'/penguin.ini',QSettings.IniFormat))
            w.timer.stop()
            w.change_type('penguin')
            self.assertEqual(w.pet.skin,'classic_penguin')
            w.change_pet('blue_penguin')
            w.change_type('fox')
            w.change_type('penguin')
            self.assertEqual(w.pet.skin,'blue_penguin')
            menu=QMenu(w)
            w.populate_menu(menu)
            petmenu=menu.actions()[0].menu()
            self.assertEqual([a.text() for a in petmenu.actions()[1].menu().actions()],['Classic','Blue'])
            w.close()
            if w.tray:
                w.tray.hide()
            app.aboutToQuit.disconnect(w.save_settings)
            app.screenAdded.disconnect(w.screen_changed)
            app.screenRemoved.disconnect(w.screen_changed)

    def test_every_pose_and_hop_frame(self):
        pet=PetEngine()
        states=['idle','happy','sliding','walking','sleeping','climbing','angry','held']
        sheet=QImage(130*len(states),320,QImage.Format_ARGB32)
        sheet.fill(QColor('#343744'))
        painter=QPainter(sheet)
        painter.setFont(QFont('Segoe UI',10))
        for row,skin in enumerate(('classic_penguin','blue_penguin')):
            pet.set_skin(skin)
            for direction in (-1,1):
                pet.facing=direction
                for frame in range(8):
                    pet.walk_phase=frame
                    for state in states+['blink','groom','stretch','drowsy','slipping','landing','wall_look','sniff']:
                        pet.running=state=='sliding'
                        pet.state='walking' if state=='sliding' else state
                        img=QImage(130,150,QImage.Format_ARGB32)
                        img.fill(Qt.transparent)
                        p=QPainter(img)
                        pet.draw(p,8,48)
                        p.end()
                        self.assertTrue(any(img.pixelColor(x,y).alpha() for y in range(150) for x in range(130)))
            pet.facing=1
            pet.walk_phase=3
            pet.sleep_progress=1
            for col,state in enumerate(states):
                pet.running=state=='sliding'
                pet.state='walking' if state=='sliding' else state
                pet.draw(painter,col*130+8,row*160+40)
                painter.setPen(QColor('white'))
                painter.drawText(col*130+5,row*160+18,state)
        painter.end()
        Path('artifacts').mkdir(exist_ok=True)
        sheet.save('artifacts/penguin-poses.png')

if __name__ == '__main__':
    unittest.main()
