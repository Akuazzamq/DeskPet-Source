"""Species-specific, interruptible antics and bounded pixel effects."""
import math
import random
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPen, QPolygon, QPainter

TRAIL_TYPES = {'penguin', 'axolotl'}
DURATIONS = {'cat': 3.2, 'fox': 2.6, 'rabbit': 3.0, 'gorilla': 2.6,
             'dog': 3.2, 'panda': 4.0, 'duck': 3.0, 'dragon': 2.8}


class SpecialActions:
    def __init__(self):
        self.rng = random.Random()
        self.wait = 8.0
        self.elapsed = 0.0
        self.active = False
        self.last = None
        self.skin = None

    def tick(self, behavior, now):
        pet = behavior.pet
        dt = min(.1, max(0, now - self.last)) if self.last is not None else 0
        self.last = now
        if self.skin != pet.skin:
            self.skin = pet.skin
            self.active = False
            self.wait = 8.0
        species = pet.get_pet_type()
        allowed = (behavior.taskbar and behavior.wander) or species == 'dragon'
        if not allowed or (self.active and pet.state != 'special'):
            self.active = False
            pet.special_progress = 0
            self.wait = max(self.wait, 5.0)
            if pet.state == 'special':
                behavior.enter('idle')
        if self.active:
            self.elapsed += dt
            pet.special_progress = min(1, self.elapsed / DURATIONS[species])
            if pet.special_progress >= 1:
                self.active = False
                behavior.enter('walking' if behavior.taskbar and behavior.wander else 'idle', 3 if behavior.taskbar else 0)
                behavior.next_walk = now + .1
                behavior.next_action = now + 4
                self.wait = self.rng.uniform(24, 38)
            return True
        self.wait = max(0, self.wait - dt)
        ready = pet.state == 'walking' or (species == 'dragon' and pet.state in ('idle', 'curious'))
        if allowed and ready and species in DURATIONS and self.wait <= 0:
            behavior.enter('special')
            self.active = True
            self.elapsed = 0
            pet.special_progress = 0
            return True
        return False


def draw_special(pet, p, x, y, draw_base):
    species = pet.get_pet_type()
    special = pet.state == 'special'
    trail = pet.taskbar_effects and pet.state == 'walking' and species in TRAIL_TYPES
    if not special and not trail:
        draw_base(p, x, y)
        return
    t = pet.special_progress
    wave = math.sin(t * math.pi * 8)
    original = pet.state
    p.save()
    if special:
        pet.state = {'panda':'groom', 'rabbit':'groom', 'gorilla':'idle',
                     'cat':'groom', 'fox':'curious', 'dog':'happy', 'duck':'happy',
                     'dragon':'idle'}[species]
        if species == 'panda' and t < .3:
            pet.state = 'idle'
        if species in ('fox', 'dog'):
            p.translate(round(wave*3), -round(max(0, math.sin(t*math.pi*4))*5))
        elif species == 'gorilla':
            p.translate(round(wave*2), 0)
        elif species == 'dragon':
            p.translate(0, round(math.sin(t*math.pi)*2))
    elif species == 'axolotl':
        p.translate(0, -round(3 + 2*math.sin(pet.effect_phase)))
    try:
        draw_base(p, x, y)
    finally:
        pet.state = original
        p.restore()
    p.save()
    p.translate(x, y)
    p.setRenderHint(QPainter.Antialiasing, False)

    def poly(points, color):
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(color))
        p.drawPolygon(QPolygon([QPoint(round(a),round(b)) for a,b in points]))

    def line(points, color, width=2):
        p.setPen(QPen(QColor(color),width,Qt.SolidLine,Qt.SquareCap,Qt.MiterJoin))
        p.drawPolyline(QPolygon([QPoint(round(a),round(b)) for a,b in points]))

    def pixel(a,b,size,color):
        p.fillRect(round(a),round(b),size,size,QColor(color))

    if trail:
        if pet.facing < 0:
            p.translate(114,0)
            p.scale(-1,1)
        for i in range(7):
            age=(pet.effect_phase*.6+i/7)%1
            a=30-age*27
            b=79-age*(16 if species=='axolotl' else 6)+(i%2)*2
            p.setOpacity((1-age)*.65)
            if species=='penguin':
                poly([(a,b-3),(a+3,b),(a,b+3),(a-2,b)],'#B9EBFF')
                pixel(a,b,2,'#F1FCFF')
            else:
                p.setPen(QPen(QColor('#8CD9ED'),1))
                p.setBrush(Qt.NoBrush)
                p.drawRect(round(a),round(b),3,3)
        p.restore()
        return
    if species == 'panda':
        growth=min(1,t/.3)
        top=83-48*growth
        # The stalk sprouts first, then shortens as the panda nibbles.
        if t>.55:
            top += int((t-.55)*5)*7
        line([(86,82),(86,top)],'#54823F',5)
        for b in range(45,80,10):
            if b>top:
                line([(83,b),(89,b)],'#B0D579',2)
                poly([(86,b),(96,b-8),(99,b-8),(95,b-2)],'#83B957')
        if t>.35:
            for i in range(3):
                pixel(61+i*4,58+((t*45+i*4)%13),2,'#A7CE6C')
    elif species == 'rabbit':
        bite=min(3,int(t*4))
        poly([(62,59+bite*3),(77,62+bite*3),(66,80)],'#ED943B')
        line([(68,61+bite*3),(69,53+bite*3)],'#73AA50',3)
        line([(69,58+bite*3),(76,54+bite*3)],'#92C366',2)
        line([(65,66+bite*2),(70,68+bite*2)],'#B76B33',1)
    elif species == 'cat':
        a=77+wave*12
        poly([(a-8,76),(a-5,69),(a+4,68),(a+9,75),(a+7,82),(a-5,83)],'#D991BB')
        line([(a-5,73),(a+5,79),(a-3,80),(a+4,72)],'#F6CBE2',1)
        line([(a-7,79),(62,82),(54,77)],'#D991BB',1)
    elif species == 'fox':
        a=85+math.sin(t*9)*12; b=42+abs(math.cos(t*7))*34
        poly([(a,b-8),(a+7,b),(a+2,b+6),(a-6,b+3)],'#DFA347')
        line([(a-3,b+5),(a+3,b-3)],'#826040',1)
    elif species == 'dog':
        a=80+wave*14; b=79-abs(math.sin(t*math.pi*4))*14
        poly([(a-6,b-6),(a+4,b-6),(a+8,b),(a+4,b+6),(a-6,b+6),(a-9,b)],'#83B967')
        line([(a-3,b-5),(a+2,b),(a-2,b+5)],'#EFF1CA',2)
    elif species == 'gorilla':
        c=pet.pets[pet.skin]['colors']
        for i,a in enumerate((41,65)):
            b=60+round(math.sin(t*math.pi*12+i*math.pi)*5)
            poly([(a-7,b),(a+5,b-2),(a+9,b+7),(a+2,b+12),(a-8,b+8)],c['body'])
            line([(a-4,b+2),(a+3,b+2)],c['highlight'],2)
            if (wave>0)==(i==0):
                line([(a-6,b+14),(a-10,b+17)],'#E6C686',2)
    elif species == 'duck':
        p.setOpacity(.55)
        for i in range(3):
            r=7+((t*24+i*7)%22)
            line([(56-r,82),(56,84),(56+r,82)],'#8BD7EB',1)
        for i in range(5):
            a=23+i*17; h=abs(math.sin(t*16+i))*12
            pixel(a,80-h,2,'#A7EBF4')
        p.setOpacity(1)
    elif species == 'dragon':
        # Front-facing mouth emits a small curling flame inside the pet canvas.
        strength=math.sin(math.pi*t)**.7
        if strength>.1:
            end=70+39*strength
            poly([(61,54),(77,51),(84,43),(87,50),(end,41+wave*2),
                  (end-5,56),(end,63),(82,65),(69,59)],'#E87538')
            poly([(62,54),(79,54),(end-5,49),(end-9,59),(78,60)],'#FFC65B')
            poly([(63,54),(79,55),(87,53),(80,58)],'#FFF0B0')
            for i in range(3):
                pixel(91+i*6,40+((t*30+i*7)%20),2,'#F4B657')
    p.restore()
