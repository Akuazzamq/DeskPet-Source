import unittest
from pathlib import Path
from test_behavior import app
from pet_engine import PetEngine
from behavior import Behavior
from PySide6.QtGui import QImage,QPainter,QColor
from PySide6.QtCore import Qt

class BirdAnimationTests(unittest.TestCase):
    def test_reactions_have_multiple_frames(self):
        sheet=QImage(8*130,8*130,QImage.Format_ARGB32)
        sheet.fill(QColor('#343744'))
        out=QPainter(sheet)
        row=0
        for skin in ('normal_duck','azzamq_duck','classic_penguin','blue_penguin'):
            pet=PetEngine();pet.set_skin(skin)
            for state in ('happy','groom'):
                frames=[]
                pet.state=state
                for phase in range(8):
                    pet.animation_phase=phase
                    img=QImage(130,120,QImage.Format_ARGB32);img.fill(Qt.transparent)
                    p=QPainter(img);pet.draw(p,8,12);p.end()
                    frames.append(bytes(img.constBits()))
                    out.drawImage(phase*130,row*130,img)
                self.assertGreaterEqual(len(set(frames)),4,(skin,state))
                row+=1
        out.end()
        Path('artifacts').mkdir(exist_ok=True)
        sheet.save('artifacts/bird-animation-frames.png')

    def test_held_clock_and_pause(self):
        for skin in ('normal_duck','classic_penguin'):
            pet=PetEngine();pet.set_skin(skin)
            behavior=Behavior(pet,now=0)
            behavior.enter('held')
            behavior.tick(.25,0)
            self.assertEqual(pet.animation_phase,2)
            self.assertEqual(pet.state,'held')
            behavior.paused=True
            behavior.tick(.5,0)
            self.assertEqual(pet.animation_phase,2)

if __name__=='__main__':
    unittest.main()
