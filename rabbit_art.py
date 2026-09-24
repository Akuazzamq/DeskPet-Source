"""Rabbit pixel artwork: sitting, hopping, folded-ear sleep and wall antics."""
import math
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPen, QPolygon, QPainter


def draw_rabbit(pet, p, x, y):
    c = pet.pets[pet.skin]['colors']
    panda = pet.skin == 'panda_rabbit'
    state = pet.state
    phase = pet.walk_phase % 8
    sleeping = state in ('sleeping', 'drowsy')
    hopping = state == 'walking'
    climbing = state in ('climbing', 'slipping')
    side = hopping or climbing or state in ('wall_look', 'landing', 'angry')
    b = pet.idle_frame
    p.save()
    p.translate(x, y)
    p.setRenderHint(QPainter.Antialiasing, False)
    if side and pet.facing < 0:
        p.translate(114, 0)
        p.scale(-1, 1)

    def shape(points, color, border=True):
        p.setPen(QPen(c['outline'], 3, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin) if border else Qt.NoPen)
        p.setBrush(color)
        p.drawPolygon(QPolygon([QPoint(round(a), round(b)) for a, b in points]))

    def line(points, color, width=2):
        p.setPen(QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPolyline(QPolygon([QPoint(round(a), round(b)) for a, b in points]))

    def dot(a, b, w, h, color):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawRect(round(a), round(b), w, h)

    def tail(a, b):
        shape([(a,b+4),(a+4,b),(a+10,b),(a+14,b+5),(a+12,b+12),(a+5,b+14),(a,b+10)], c['body'])

    def ear(a, base, lean, height, dark=False):
        shape([(a,base),(a+lean-2,base-height+6),(a+lean+1,base-height),
               (a+lean+7,base-height),(a+lean+11,base-height+7),(a+12,base)],
              c['patch'] if dark else c['body'])
        line([(a+6,base-5),(a+lean+4,base-height+7)], c['ear'], 4)

    def eye(a, b, closed=False, angry=False):
        if panda:
            shape([(a-3,b-2),(a+6,b-3),(a+9,b+3),(a+6,b+11),(a-3,b+9),(a-5,b+4)],c['patch'],False)
        ink = QColor('#FFF5E8') if panda else c['eye']
        if angry:
            line([(a-1,b+2),(a+6,b+5)],ink,2)
        elif closed:
            line([(a-1,b+4),(a+2,b+6),(a+6,b+4)],ink,2)
        else:
            dot(a,b,5,8,c['eye'])
            dot(a+1,b,2,2,QColor('#FFF9F3'))

    # Sleep: tucked feet, rounded body and long ears laid over the back.
    if sleeping:
        t = 1 if state == 'sleeping' else pet.sleep_progress
        breathe = round((1-math.cos(pet.breath_phase))*.75) if state == 'sleeping' else 0
        tail(87,65)
        shape([(32,65),(38,51-breathe),(52,44-breathe),(73,45-breathe),
               (89,54-breathe),(94,69),(86,79),(43,81),(29,75)],c['body'])
        shape([(22,76),(29,72),(46,73),(50,80),(42,83),(24,82)],c['patch'])
        head_y=round(t*7)
        shape([(22,52+head_y),(29,45+head_y),(43,45+head_y),(55,53+head_y),
               (55,66+head_y),(45,74+head_y),(29,73+head_y),(19,63+head_y)],c['body'])
        shape([(30,49+head_y),(44,40),(69,43),(76,48),(69,53),(45,50),(34,55+head_y)],c['patch'] if panda else c['body'])
        line([(40,46),(65,47)],c['ear'],3)
        shape([(41,51+head_y),(57,43),(81,48),(85,54),(77,57),(54,52),(44,57+head_y)],c['patch'] if panda else c['body'])
        line([(52,49),(76,52)],c['ear'],3)
        eye(27,58+head_y,True)
        eye(44,58+head_y,True)
        dot(36,67+head_y,4,2,c['ear'])
        if state == 'sleeping':
            rise=round(pet.breath_phase/(2*math.pi)%1*4)
            for a,b0,k in [(77,31-rise,4),(88,22-rise,5)]:
                line([(a,b0),(a+k,b0),(a,b0+k),(a+k,b0+k)],QColor('#D8DDEA'),1)
        p.restore()
        return

    if side:
        # Both hind legs compress, push off and tuck together on each hop.
        lift=(0,1,5,9,11,8,4,0)[phase] if hopping else 0
        if hopping and pet.running:
            lift=round(lift*1.2)
        if state == 'landing':
            p.translate(0,84)
            p.scale(1,.84)
            p.translate(0,-84)
        if state == 'angry':
            lift=b*2  # tiny hind-foot stomp
        if climbing:
            p.translate(8,-2)
            p.translate(60,65)
            p.rotate(-28 if state == 'climbing' else -12)
            p.translate(-60,-65)
        tail(21,61-lift)
        shape([(34,65-lift),(38,51-lift),(49,44-lift),(67,44-lift),
               (81,52-lift),(82,67-lift),(71,77-lift),(44,77-lift)],c['body'])
        shape([(39,59-lift),(47,53-lift),(58,56-lift),(62,66-lift),
               (55,75-lift),(41,74-lift)],c['patch'],False)
        # Big hind paw and paired little forepaws.
        tuck = 8 if hopping and phase in (2,3,4,5) else 0
        if climbing:
            tuck = (0,3,6,3,0,-3,-6,-3)[phase]
        shape([(43,67-lift),(52,69-lift),(56+tuck,78-lift),(51+tuck,83-lift),
               (32+tuck,83-lift),(30+tuck,79-lift)],c['body'])
        line([(36+tuck,80-lift),(47+tuck,80-lift)],c['patch'],3)
        shape([(69,64-lift),(77,63-lift),(84-tuck,78-lift),(91-tuck,80-lift),
               (90-tuck,83-lift),(79-tuck,83-lift),(70,73-lift)],c['body'])
        # Ears trail back in flight but remain inside the sprite bounds.
        lean = -8 if lift>4 else -3
        ear(63, 37-lift, lean-4, 25, panda)
        ear(75,37-lift,lean,30 if lift<5 else 23,panda)
        shape([(62,37-lift),(71,31-lift),(87,32-lift),(96,40-lift),
               (99,51-lift),(91,60-lift),(74,61-lift),(62,53-lift)],c['body'])
        eye(84,40-lift,state=='wall_look',state=='angry')
        dot(97,49-lift,4,3,c['ear'])
        line([(98,53-lift),(94,55-lift)],c['outline'],1)
        line([(78,52-lift),(82,53-lift)],c['blush'],2)
        if state=='angry':
            line([(46,26),(51,26),(51,21)],QColor('#F07868'),2)
            line([(56,21),(56,26),(61,26)],QColor('#F07868'),2)
        p.restore()
        return

    # Seated front pose; long ears carry most of the rabbit's expression.
    if state=='held':
        p.translate(0,-2)
    elif state=='stretch':
        p.translate(0,-1)
    tail(76,67)
    shape([(35,71),(38,57),(47,48),(62,48),(72,58),(78,73),
           (73,81),(39,81)],c['body'])
    shape([(47,56),(61,56),(66,68),(59,77),(47,74),(43,65)],c['patch'],False)
    for a in (34,62):
        end=87 if state=='held' else 83
        shape([(a+3,72),(a+10,72),(a+14,end-4),(a+10,end),(a-2,end),(a-4,end-3)],c['body'])
        line([(a,end-2),(a+8,end-2)],c['patch'],3)
    p.save()
    if state=='curious':
        p.translate(pet.curious_direction*2,0)
    lean=-3 if pet.ear_twitch or state=='look' else 0
    ear(35,37,-5+lean,32,panda)
    ear(59,37,5-lean,34,panda)
    shape([(28,42),(35,33),(48,30),(65,31),(77,39),(81,50),
           (76,61),(65,67),(44,67),(32,61),(26,51)],c['body'])
    closed=state in ('blink','groom','happy','stretch')
    look=pet.curious_direction if state=='curious' else 0
    eye(37+look,43,closed)
    eye(64+look,43,closed)
    nose=1 if state=='sniff' or b else 0
    shape([(51,55+nose),(57,55+nose),(54,58+nose)],c['ear'],False)
    line([(54,59),(54,61),(50,62)],c['outline'],1)
    line([(54,61),(58,62)],c['outline'],1)
    dot(52,62,4,3,QColor('#FFFDF5'))
    line([(32,55),(37,56)],c['blush'],3)
    line([(71,56),(76,55)],c['blush'],3)
    p.restore()
    if state=='groom':
        shape([(38,70),(34,52-b*3),(38,48-b*3),(44,50-b*3),(46,67)],c['body'])
    if state=='happy':
        shape([(89,34),(86,30),(87,26),(91,25),(94,28),(97,25),
               (101,26),(102,30),(94,38)],c['blush'],False)
    p.restore()
