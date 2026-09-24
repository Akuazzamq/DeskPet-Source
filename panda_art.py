"""Round, stepped pixel pandas with a bamboo-snacking idle pose."""
import math
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPainter, QPen, QPolygon


def draw_panda(pet, p, x, y):
    c = pet.pets[pet.skin]['colors']
    state = pet.state
    phase = pet.walk_phase % 8
    sleepy = state in ('sleeping', 'drowsy')
    side = state in ('walking', 'wall_look', 'climbing', 'slipping', 'landing')
    p.save()
    p.translate(x, y)
    p.setRenderHint(QPainter.Antialiasing, False)
    if side and pet.facing < 0:
        p.translate(114, 0)
        p.scale(-1, 1)

    def shape(points, color, border=True):
        p.setPen(QPen(c['outline'], 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin) if border else Qt.NoPen)
        p.setBrush(color)
        p.drawPolygon(QPolygon([QPoint(round(a), round(b)) for a,b in points]))

    def line(points, color, width=2):
        p.setPen(QPen(color,width,Qt.SolidLine,Qt.SquareCap,Qt.MiterJoin))
        p.drawPolyline(QPolygon([QPoint(round(a),round(b)) for a,b in points]))

    def roundbit(a,b,w,h,color):
        shape([(a+5,b),(a+w-5,b),(a+w,b+5),(a+w,b+h-5),
               (a+w-5,b+h),(a+5,b+h),(a,b+h-5),(a,b+5)],color)

    def eye(a,b,mirror=False):
        shape([(a,b+4),(a+4,b),(a+10,b+1),(a+13,b+7),(a+10,b+14),
               (a+4,b+15),(a-2,b+10)],c['dark'],False)
        if sleepy or state in ('happy','blink'):
            line([(a+2,b+7),(a+5,b+9),(a+9,b+7)],c['body'],2)
        else:
            p.fillRect(a+4,b+5,5,6,c['body'])
            p.fillRect(a+(4 if mirror else 6),b+6,3,4,c['outline'])
            p.fillRect(a+5,b+5,2,2,QColor('#FFFFFF'))

    def face(a,b):
        eye(a,b)
        eye(a+29,b,True)
        shape([(a+17,b+14),(a+23,b+14),(a+22,b+18),(a+19,b+18)],c['outline'],False)
        line([(a+20,b+18),(a+20,b+21),(a+16,b+23),(a+12,b+21)],c['outline'],1)
        line([(a+20,b+21),(a+24,b+23),(a+28,b+21)],c['outline'],1)
        p.fillRect(a-1,b+17,7,3,c['blush'])
        p.fillRect(a+35,b+17,7,3,c['blush'])
        if state=='angry':
            line([(a,b+2),(a+10,b+5)],c['outline'],3)
            line([(a+30,b+5),(a+40,b+2)],c['outline'],3)

    if sleepy:
        breath=round((1-math.cos(pet.breath_phase))*.8)
        roundbit(40,49-breath,52,34+breath,c['body'])
        roundbit(69,56,23,26,c['dark'])
        roundbit(26,48,17,17,c['dark'])
        roundbit(53,43,17,17,c['dark'])
        p.save()
        p.translate(0,3 if state=='sleeping' else round(pet.sleep_progress*3))
        roundbit(22,53,49,25,c['body'])
        eye(26,57)
        eye(51,57,True)
        p.fillRect(43,70,5,3,c['outline'])
        p.restore()
        roundbit(23,76,26,8,c['dark'])
        roundbit(58,77,22,7,c['dark'])
        if state=='sleeping':
            for a,b in ((78,31),(91,21)):
                line([(a,b),(a+5,b),(a,b+5),(a+5,b+5)],QColor('#DCE4EF'),1)
        p.restore()
        return

    if state=='walking':
        p.translate(0,-(0,1,2,1,0,1,2,1)[phase]*(2 if pet.running else 1))
    elif state in ('climbing','slipping'):
        p.translate(66,62)
        p.rotate(-30 if state=='climbing' else -12)
        p.translate(-66,-62)
    elif state=='held':
        p.translate(56,53)
        p.rotate(5 if pet.idle_frame else -5)
        p.translate(-56,-53)
    elif state in ('stretch','settle','landing'):
        p.translate(0,84)
        p.scale(.94 if state=='stretch' else 1.06,1.1 if state=='stretch' else .88)
        p.translate(0,-84)

    if side:
        step=(0,3,5,3,0,-3,-5,-3)[phase]
        roundbit(20,61,13,13,c['body'])
        for a,delta in ((37,-step),(75,step)):
            roundbit(a+delta,65,14,19,c['dark'])
        shape([(29,62),(34,48),(47,41),(64,43),(79,52),(84,67),
               (76,76),(42,77),(30,72)],c['body'])
        shape([(62,45),(76,50),(83,62),(80,73),(65,76),(59,65)],c['dark'])
        roundbit(66,24,17,18,c['dark'])
        roundbit(86,26,15,16,c['dark'])
        shape([(63,38),(72,31),(90,32),(100,41),(100,50),(108,54),
               (107,64),(98,69),(78,67),(66,59),(60,47)],c['body'])
        eye(83,42)
        p.fillRect(102,55,5,4,c['outline'])
        line([(98,63),(104,62)],c['outline'],1)
        p.fillRect(87,59,7,3,c['blush'])
        roundbit(37+step,68,17,16,c['dark'])
        if state in ('climbing','wall_look'):
            roundbit(80,58,21,12,c['dark'])
        else:
            roundbit(73-step,65,16,19,c['dark'])
    else:
        roundbit(75,69,13,13,c['body'])
        shape([(33,61),(40,51),(66,51),(77,61),(81,73),(76,81),
               (65,85),(43,85),(31,80),(27,70)],c['dark'])
        shape([(42,56),(63,56),(72,66),(72,76),(63,81),(45,81),(36,74),(36,64)],c['body'])
        shape([(42,74),(51,77),(66,75),(62,80),(46,80)],c['shade'],False)
        for a in (29,65):
            roundbit(a,73,21,16 if state=='held' else 12,c['dark'])
            p.fillRect(a+6,78,7,3,c['pad'])
        p.save()
        if state in ('curious','look'):
            p.translate(pet.curious_direction*2,-pet.idle_frame)
        if state=='sniff':
            p.translate(0,pet.idle_frame*2)
        roundbit(23,15-pet.idle_frame,20,20,c['dark'])
        roundbit(68,15,20,20,c['dark'])
        roundbit(28,20-pet.idle_frame,9,8,c['pad'])
        roundbit(73,20,9,8,c['pad'])
        shape([(29,31),(38,23),(50,21),(66,22),(78,28),(85,39),(86,49),
               (80,59),(69,65),(42,65),(29,59),(23,48),(24,38)],c['body'])
        shape([(30,52),(41,60),(69,60),(79,54),(73,63),(42,63)],c['shade'],False)
        face(34,36)
        p.restore()
        if state=='groom':
            # Existing grooming idle becomes the panda's bamboo snack.
            chew=pet.idle_frame*2
            line([(46,80),(66,50+chew)],QColor('#426B3C'),5)
            line([(47,79),(66,51+chew)],QColor('#8FC15C'),2)
            for a,b in ((51,73),(57,65),(63,57)):
                line([(a-2,b-1),(a+2,b+1)],QColor('#C9DE84'),2)
            shape([(63,57),(69,43),(76,42),(72,51)],QColor('#73A850'),False)
            shape([(60,63),(48,54),(48,48),(58,54)],QColor('#8ABF5B'),False)
            roundbit(30,61,23,12,c['dark'])
            roundbit(64,58+chew,18,13,c['dark'])
        else:
            for a in (28,70):
                roundbit(a,60,14,17,c['dark'])
    if state=='happy':
        shape([(91,20),(94,17),(97,20),(100,17),(103,20),(103,24),(97,30),(91,24)],c['blush'],False)
    p.restore()
