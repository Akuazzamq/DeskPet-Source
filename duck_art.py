"""Pixel ducks, including the blue-cap and purple-shades AzzamQ mascot."""
import math
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPainter, QPen, QPolygon


def draw_duck(pet, p, x, y):
    c = pet.pets[pet.skin]['colors']
    branded = pet.skin == 'azzamq_duck'
    state = pet.state
    phase = pet.walk_phase % 8
    action = pet.animation_phase % 8
    flutter = (0, 3, 7, 10, 7, 3, 0, -2)[action]
    sway = (0, 1, 2, 1, 0, -1, -2, -1)[action]
    asleep = state in ('sleeping', 'drowsy')
    side = state in ('walking', 'wall_look', 'climbing', 'slipping', 'landing')
    p.save()
    p.translate(x, y)
    p.setRenderHint(QPainter.Antialiasing, False)

    def shape(points, color, border=True):
        p.setPen(QPen(c['outline'], 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin) if border else Qt.NoPen)
        p.setBrush(color)
        p.drawPolygon(QPolygon([QPoint(round(a),round(b)) for a,b in points]))

    def line(points, color, width=2):
        p.setPen(QPen(color,width,Qt.SolidLine,Qt.SquareCap,Qt.MiterJoin))
        p.drawPolyline(QPolygon([QPoint(round(a),round(b)) for a,b in points]))

    def cap(a,b,profile=False):
        shape([(a+4,b+17),(a+6,b+7),(a+14,b),(a+30,b-2),(a+43,b+3),
               (a+49,b+12),(a+49,b+24),(a+27,b+20)],QColor('#1265D8'))
        shape([(a+30,b+1),(a+40,b+6),(a+43,b+20),(a+49,b+24),
               (a+49,b+12),(a+43,b+3)],QColor('#123DAC'),False)
        line([(a+10,b+12),(a+14,b+6),(a+27,b+2)],QColor('#43BDF5'),2)
        shape([(a-9,b+16),(a+12,b+13),(a+34,b+18),(a+50,b+23),
               (a+51,b+28),(a+25,b+22),(a+4,b+21),(a-10,b+20)],QColor('#1647B8'))
        p.fillRect(a+25,b-4,7,3,QColor('#169DEE'))

    def shades(a,b,profile=False):
        if profile:
            shape([(a,b),(a+19,b+1),(a+17,b+15),(a+4,b+15),(a,b+10)],QColor('#39215F'))
            line([(a+9,b+3),(a+4,b+12)],QColor('#B875DC'),3)
            line([(a-10,b+1),(a,b+3)],c['outline'],4)
        else:
            for offset in (0,28):
                shape([(a+offset,b),(a+offset+22,b),(a+offset+20,b+14),
                       (a+offset+15,b+18),(a+offset+6,b+17),(a+offset+2,b+12)],QColor('#39215F'))
                line([(a+offset+12,b+3),(a+offset+5,b+12)],QColor('#B875DC'),4)
                line([(a+offset+17,b+3),(a+offset+11,b+12)],QColor('#7745A9'),2)
            line([(a+21,b+4),(a+28,b+4)],c['outline'],4)
        line([(a,b),(a+(19 if profile else 49),b)],QColor('#454760'),2)

    def chain(a,b,profile=False):
        for dx,dy in ([(0,0),(5,5),(11,7),(17,5)] if profile else [(0,0),(5,6),(13,10),(22,10),(30,6),(35,0)]):
            line([(a+dx,b+dy),(a+dx+3,b+dy+3),(a+dx+7,b+dy+1)],QColor('#ED9C16'),4)
            line([(a+dx,b+dy-1),(a+dx+4,b+dy+1)],QColor('#FFE479'),2)

    def eye(a,b):
        if asleep or state in ('blink','happy'):
            line([(a,b),(a+3,b+2),(a+7,b)],c['eye'],2)
        else:
            p.fillRect(a,b,5,7,c['eye'])
            p.fillRect(a+1,b,2,2,QColor('#FFFFFF'))

    if side and pet.facing < 0:
        p.translate(114,0)
        p.scale(-1,1)
    if asleep:
        breath=round((1-math.cos(pet.breath_phase))*.8)
        shape([(24,71),(20,60),(33,64),(42,52-breath),(66,49-breath),
               (86,59),(94,73),(83,83),(40,84),(28,79)],c['body'])
        shape([(55,65),(71,62),(83,69),(78,77),(61,79),(51,73)],c['wing'])
        p.save()
        p.translate(0,3 if state=='sleeping' else round(pet.sleep_progress*3))
        shape([(24,54),(28,43),(42,38),(56,42),(63,54),(60,66),
               (50,73),(32,71),(23,64)],c['head'])
        if branded:
            cap(16,22)
            # Shades pushed up while napping so the closed eye remains visible.
            line([(28,49),(49,50)],QColor('#7B4DB0'),4)
        eye(32,57)
        shape([(27,64),(44,63),(50,68),(46,73),(26,72),(22,68)],c['bill'])
        line([(26,69),(43,69)],c['bill_shadow'],1)
        p.restore()
        if state=='sleeping':
            for a,b in ((81,34),(94,23)):
                line([(a,b),(a+5,b),(a,b+5),(a+5,b+5)],QColor('#DCE5EF'),1)
        p.restore()
        return
    if state in ('idle', 'blink', 'curious', 'look', 'groom', 'happy', 'angry'):
        p.translate(56, 84)
        p.scale(1, 1 + sway * .006)
        if state == 'happy':
            p.translate(0, -max(0, flutter) * .35)
        elif state == 'angry':
            p.rotate(sway * 1.5)
        p.translate(-56, -84)
    if state=='walking':
        p.translate(0,-(0,1,3,1,0,1,3,1)[phase])
        p.translate(56,80)
        p.rotate((0,-2,-3,-2,0,2,3,2)[phase])
        p.translate(-56,-80)
    elif state in ('climbing','slipping'):
        p.translate(65,62)
        p.rotate(-28 if state=='climbing' else -10)
        p.translate(-65,-62)
    elif state=='held':
        p.translate(55,51)
        p.rotate(sway * 2)
        p.translate(-55,-51)
    elif state in ('stretch','settle','landing'):
        p.translate(0,84)
        p.scale(.94 if state=='stretch' else 1.06,1.1 if state=='stretch' else .88)
        p.translate(0,-84)

    if side:
        step=(0,3,5,3,0,-3,-5,-3)[phase] * (1.4 if pet.running and state=='walking' else 1)
        for a,delta in ((44,-step),(68,step)):
            shape([(a+delta,72),(a+6+delta,72),(a+7+delta,79),
                   (a+16+delta,81),(a+16+delta,84),(a-3+delta,84)],c['bill'])
        shape([(32,65),(19,52),(18,65),(27,75),(39,80),(62,79),
               (79,69),(80,52),(66,43),(46,48)],c['body'])
        p.save()
        p.translate(49, 58)
        p.rotate((step * 3 if pet.running else step) if state=='walking' else flutter)
        p.translate(-49, -58)
        shape([(37,59),(52,53),(65,58),(64,68),(51,74),(39,71)],c['wing'])
        line([(40,64),(47,68),(56,66)],c['shade'],1)
        p.restore()
        shape([(63,25),(74,20),(89,25),(95,35),(95,50),(88,59),
               (73,61),(63,52),(58,40)],c['head'])
        if branded:
            cap(48,7,True)
            shades(77,35,True)
            chain(65,58,True)
            line([(40,66),(54,66)],QColor('#EFBF35'),2)
        else:
            eye(81,35)
            shape([(67,24),(67,16),(73,20),(77,16),(79,23)],c['head'])
        shape([(91,46),(105,46),(111,50),(110,57),(102,62),(89,58),(86,52)],c['bill'])
        line([(94,55),(108,54)],c['bill_shadow'],2)
        p.fillRect(102,49,2,2,c['bill_shadow'])
        if state=='climbing':
            shape([(61,58),(73,54),(81,46),(87,49),(78,63),(65,68)],c['wing'])
    else:
        shape([(74,66),(88,59),(86,71),(76,78)],c['body'])
        for a in (34,63):
            end=89 if state=='held' else 84
            shape([(a+3,73),(a+11,73),(a+13,end-5),(a+19,end-3),
                   (a+19,end),(a-3,end),(a-4,end-3)],c['bill'])
            line([(a+7,end-3),(a+7,end)],c['bill_shadow'],1)
        shape([(36,53),(47,48),(64,48),(76,57),(81,69),(77,77),
               (66,82),(43,82),(31,75),(29,65)],c['body'])
        shape([(42,64),(64,61),(70,69),(64,77),(47,77),(39,72)],c['wing'],False)
        if branded:
            chain(34,58)
            # Small AQ monogram stays legible at sprite size.
            line([(48,76),(50,71),(52,76),(49,74),(52,74)],QColor('#F4D4AF'),1)
            line([(56,71),(59,71),(60,75),(56,75),(56,71),(61,77)],QColor('#F4D4AF'),1)
        p.save()
        if state in ('curious','look'):
            p.translate(pet.curious_direction*2,-pet.idle_frame)
        elif state=='groom' and not branded:
            p.translate(55, 54)
            p.rotate(-8 - flutter*.6)
            p.translate(-55, -54)
        elif state=='sniff':
            p.translate(0,pet.idle_frame*2)
        shape([(28,30),(37,21),(53,18),(70,22),(81,31),(84,44),
               (79,55),(69,62),(41,62),(29,56),(23,44)],c['head'])
        if branded:
            shape([(28,29),(33,25),(37,30),(42,25),(47,30),(53,25),
                   (60,31),(66,27),(75,34),(79,43),(78,27),(31,21)],c['outline'],False)
            cap(23,5 - (max(0, sway) if state=='groom' else 0))
            shades(29,34 - (max(0, sway) if state=='groom' else 0))
        else:
            shape([(44,21),(44,13),(50,17),(57,12),(58,21)],c['head'])
            eye(36,35)
            eye(68,35)
            p.fillRect(28,46,8,3,c['blush'])
            p.fillRect(75,46,7,3,c['blush'])
        shape([(43,48),(52,44),(60,44),(67,48),(76,50),(78,55),
               (69,61),(43,61),(31,57),(30,53)],c['bill'])
        line([(35,56),(46,57),(63,57),(74,54)],c['bill_shadow'],2)
        p.fillRect(50,48,2,2,c['bill_shadow'])
        p.fillRect(61,48,2,2,c['bill_shadow'])
        if state=='happy' and action in (1,2,3,5,6):
            shape([(47,58),(65,58),(62,65),(55,67),(49,63)],c['bill_shadow'],False)
            p.fillRect(53,62,7,3,c['blush'])
        p.restore()
        for a in (29,72):
            raised=(state=='groom' and a==29) or state in ('happy','held','stretch')
            end=(39 + flutter if branded and state=='groom' else 48-flutter) if raised else 74+sway
            shape([(a,59),(a+7,57),(a+12,end-5),(a+9,end+2),(a+3,end+4),(a-2,end)],c['wing'])
            if branded:
                line([(a+2,end-2),(a+9,end-3)],QColor('#F4CB35'),2)
    if state=='happy':
        shape([(96,19),(99,16),(102,19),(105,16),(108,19),(108,23),(102,29),(96,23)],c['blush'],False)
    elif state=='angry':
        line([(91,25),(96,25),(96,20)],QColor('#ED8084'),2)
        line([(101,20),(101,25),(106,25)],QColor('#ED8084'),2)
    p.restore()
