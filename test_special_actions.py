import unittest
from pathlib import Path
from test_behavior import app
from pet_engine import PetEngine
from behavior import Behavior
from special_actions import DURATIONS, TRAIL_TYPES
from PySide6.QtGui import QImage,QPainter,QColor
from PySide6.QtCore import Qt

class SpecialTests(unittest.TestCase):
    def test_all_species_frames(self):
        pet=PetEngine()
        skins=list(pet.pets)
        sheet=QImage(520,115*len(skins),QImage.Format_ARGB32)
        sheet.fill(QColor('#343744'))
        out=QPainter(sheet)
        try:
            for row,skin in enumerate(skins):
                pet.set_skin(skin)
                pet.taskbar_effects=True
                pet.state='walking' if pet.get_pet_type() in TRAIL_TYPES else 'special'
                frames=[]
                for col,t in enumerate((.15,.4,.65,.85)):
                    pet.special_progress=t;pet.effect_phase=t*3
                    pet.running=True
                    img=QImage(130,110,QImage.Format_ARGB32);img.fill(Qt.transparent)
                    painter=QPainter(img)
                    try: pet.draw(painter,8,8)
                    finally: painter.end()
                    frames.append(bytes(img.constBits()))
                    out.drawImage(col*130,row*115,img)
                self.assertGreater(len(set(frames)),1,skin)
        finally: out.end()
        Path('artifacts').mkdir(exist_ok=True)
        sheet.save('artifacts/special-actions.png')

    def test_mode_interrupt_and_resume(self):
        for species in DURATIONS:
            pet=PetEngine()
            pet.set_skin(next(k for k,v in pet.pets.items() if v['type']==species))
            b=Behavior(pet,now=0);b.next_climb=999;b.next_blink=999
            b.specials.wait=0;b.specials.skin=pet.skin
            b.enter('idle');b.specials.tick(b,0)
            self.assertEqual(pet.state,'special' if species=='dragon' else 'idle')
            b.enter('walking');b.taskbar=True;b.specials.active=False;b.specials.wait=0
            self.assertTrue(b.specials.tick(b,.1))
            self.assertEqual(pet.state,'special')
            for i in range(1,60): b.specials.tick(b,.1+i*.1)
            self.assertEqual(pet.state,'walking')
            self.assertGreater(b.specials.wait,0)
            b.specials.wait=0;b.enter('walking');b.specials.tick(b,7)
            b.interact('held');b.specials.tick(b,7.1)
            self.assertFalse(b.specials.active)
            self.assertEqual(pet.state,'held')

    def test_pause_sleep_and_mode_interrupt(self):
        pet=PetEngine();pet.set_skin('classic_panda')
        b=Behavior(pet,now=0);b.taskbar=True
        b.specials.skin=pet.skin;b.specials.wait=0
        b.enter('walking');b.tick(.1,0)
        self.assertEqual(pet.state,'special')
        b.tick(.2,0);progress=pet.special_progress
        b.paused=True;b.tick(20,0)
        self.assertEqual(pet.special_progress,progress)
        b.paused=False;b.tick(20.05,0)
        self.assertLess(pet.special_progress-progress,.03)
        b.tick(20.1,200)
        self.assertEqual(pet.state,'drowsy')
        b.tick(20.2,0)
        self.assertFalse(b.specials.active)
        b.enter('walking');b.specials.wait=0;b.tick(21,0)
        self.assertEqual(pet.state,'special')
        b.taskbar=False;b.tick(21.1,0)
        self.assertNotEqual(pet.state,'special')

if __name__=='__main__': unittest.main()
