"""Chubby pixel penguins: waddling steps and a running belly slide."""
import math
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPainter, QPen, QPolygon


def draw_penguin(pet, p, x, y):
    c = pet.pets[pet.skin]['colors']
    state = pet.state
    phase = pet.walk_phase % 8
    action = pet.animation_phase % 8
    flutter = (0, 3, 7, 10, 7, 3, 0, -2)[action]
    sway = (0, 1, 2, 1, 0, -1, -2, -1)[action]
    sleeping = state in ('sleeping', 'drowsy')
    side = state in ('walking', 'wall_look', 'climbing', 'slipping', 'landing')
    slide = state == 'walking' and pet.running
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
        p.setPen(QPen(color, width, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
        p.drawPolyline(QPolygon([QPoint(round(a), round(b)) for a,b in points]))

    def eye(a,b):
        if sleeping or state in ('happy','blink'):
            line([(a,b+1),(a+3,b+3),(a+6,b+1)],c['eye'])
        else:
            p.fillRect(a,b,5,7,c['eye'])
            p.fillRect(a+1,b,2,2,QColor('#FFFFFF'))

    if sleeping or slide:
        bob = (0,1,2,1,0,1,2,1)[phase] if slide else round((1-math.cos(pet.breath_phase))*.7)
        shape([(26,70),(34,56-bob),(48,50-bob),(68,51-bob),(82,61),
               (88,74),(81,82),(37,83),(26,78)],c['body'])
        shape([(34,74),(55,69),(76,71),(83,77),(75,82),(38,82)],c['patch'],False)
        if slide:
            kick=(0,3,5,3,0,-2,-3,-2)[phase]
            shape([(32,70),(18,65-kick),(12,69-kick),(21,77),(33,79)],c['foot'])
            shape([(74,47),(88,42),(100,47),(104,57),(101,69),(90,75),(77,71),(70,61)],c['body'])
            shape([(85,50),(94,48),(99,54),(98,66),(91,70),(82,66),(81,58)],c['patch'],False)
            eye(92,54)
            shape([(101,60),(112,64),(102,69),(97,65)],c['foot'])
            shape([(52,63),(62,62),(70,70+kick),(59,76+kick),(42,75)],c['body'])
            trail=(phase*3)%9
            line([(9+trail,81),(18+trail,81)],c['shade'],1)
            line([(17+trail,77),(22+trail,77)],c['shade'],1)
        else:
            shape([(26,58),(34,49),(49,48),(61,56),(65,68),(59,77),(40,80),(27,75),(22,67)],c['body'])
            shape([(29,60),(37,55),(43,59),(50,55),(57,61),(59,71),
                   (50,76),(34,75),(27,69)],c['patch'],False)
            eye(31,63)
            eye(48,63)
            shape([(39,71),(48,71),(44,76)],c['foot'],False)
            shape([(66,64),(77,66),(79,75),(67,78),(60,73)],c['body'])
            if state=='sleeping':
                for a,b in ((77,33),(91,22)):
                    line([(a,b),(a+5,b),(a,b+5),(a+5,b+5)],QColor('#DCE6F2'),1)
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
        p.translate(56,82)
        p.rotate((0,-3,-5,-3,0,3,5,3)[phase])
        p.translate(-56,-82-(0,1,2,1,0,1,2,1)[phase])
    elif state in ('climbing','slipping'):
        p.translate(64,64)
        p.rotate(-25 if state=='climbing' else -10)
        p.translate(-64,-64)
    elif state=='held':
        p.translate(56,48)
        p.rotate(sway * 2)
        p.translate(-56,-48)
    elif state in ('stretch','settle','landing'):
        p.translate(0,84)
        p.scale(.95 if state=='stretch' else 1.06,1.08 if state=='stretch' else .88)
        p.translate(0,-84)

    if side:
        step=(0,3,5,3,0,-3,-5,-3)[phase]
        for a,delta in ((44,-step),(67,step)):
            shape([(a+delta,75),(a+7+delta,75),(a+15+delta,81),
                   (a+15+delta,84),(a-2+delta,84)],c['foot'])
        shape([(38,65),(28,70),(34,77),(43,77)],c['body'])
        shape([(40,69),(42,42),(50,27),(62,21),(77,24),(87,34),
               (91,54),(87,70),(77,79),(55,80),(43,75)],c['body'])
        shape([(71,32),(79,31),(85,40),(84,53),(86,65),(78,75),(65,76),
               (61,65),(67,51),(66,41)],c['patch'],False)
        eye(77,39)
        shape([(85,47),(99,50),(99,55),(85,58),(81,53)],c['foot'])
        line([(88,53),(96,53)],c['shade'],1)
        end=47-flutter*.5 if state=='climbing' else 70+step
        shape([(52,48),(60,50),(68,end-3),(64,end+6),(57,end+4),(49,58)],c['body'])
        line([(53,52),(59,62)],c['shade'],2)
        p.fillRect(75,52,6,3,c['blush'])
    else:
        for a in (33,63):
            end=89 if state=='held' else 84
            shape([(a+4,74),(a+11,74),(a+16,end-4),(a+17,end),
                   (a-3,end),(a-4,end-4)],c['foot'])
            line([(a+6,end-3),(a+6,end)],c['shade'],1)
        p.save()
        if state in ('curious','look'):
            p.translate(pet.curious_direction*2,-pet.idle_frame)
        elif state=='groom':
            p.translate(56, 66)
            p.rotate(-5-flutter*.6)
            p.translate(-56, -66)
        elif state=='sniff':
            p.translate(0,pet.idle_frame)
        shape([(30,65),(31,42),(35,29),(44,20),(57,17),(69,21),(78,29),
               (83,44),(85,66),(80,76),(69,81),(44,81),(33,76)],c['body'])
        # Two soft cheek lobes join the broad white belly.
        shape([(37,40),(41,31),(49,29),(56,35),(63,29),(71,31),(77,40),
               (75,52),(79,64),(76,74),(66,78),(47,78),(37,73),(35,63),
               (39,52)],c['patch'],False)
        shape([(43,71),(54,75),(70,72),(65,77),(48,77)],c['belly_shadow'],False)
        eye(43,40)
        eye(66,40)
        p.fillRect(38,51,8,3,c['blush'])
        p.fillRect(70,51,8,3,c['blush'])
        shape([(50,50),(62,50),(64,54),(57,60),(48,54)],c['foot'])
        line([(51,54),(61,54)],c['shade'],1)
        if state=='happy':
            p.fillRect(54,55,6,3,c['blush'])
        if state=='angry':
            line([(41,36),(49,39)],c['outline'],2)
            line([(65,39),(73,36)],c['outline'],2)
        p.restore()
        for a,direction in ((32,-1),(80,1)):
            raised=state in ('happy','held','stretch') or (state=='groom' and direction==-1)
            tip=43-flutter if raised else 69+sway
            if state=='groom' and direction==-1:
                tip=51-flutter*.5
            shape([(a,48),(a+direction*5,51),(a+direction*13,tip),
                   (a+direction*12,tip+8),(a+direction*6,tip+11),(a-direction*3,58)],c['body'])
            line([(a+direction*4,54),(a+direction*8,tip+5)],c['shade'],1)
    if state=='happy':
        shape([(93,20),(96,17),(99,20),(102,17),(105,20),(105,24),(99,30),(93,24)],c['blush'],False)
    p.restore()
