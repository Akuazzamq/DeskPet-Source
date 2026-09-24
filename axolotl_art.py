"""Pixel axolotl with feathery gills, tiny feet and a translucent-looking tail fin."""
import math
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPainter, QPen, QPolygon


def draw_axolotl(pet, p, x, y):
    c = pet.pets[pet.skin]['colors']
    state = pet.state
    phase = pet.walk_phase % 8
    asleep = state in ('sleeping', 'drowsy')
    side = state in ('walking', 'wall_look', 'climbing', 'slipping', 'landing')
    sway = (0, 2, 3, 2, 0, -2, -3, -2)[phase if side else pet.tail_frame * 2]
    p.save()
    p.translate(x, y)
    p.setRenderHint(QPainter.Antialiasing, False)
    if side and pet.facing < 0:
        p.translate(114, 0)
        p.scale(-1, 1)

    def shape(points, color, border=True):
        p.setPen(QPen(c['outline'], 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin) if border else Qt.NoPen)
        p.setBrush(color)
        p.drawPolygon(QPolygon([QPoint(round(a), round(b)) for a, b in points]))

    def line(points, color, width=2):
        p.setPen(QPen(color, width, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
        p.drawPolyline(QPolygon([QPoint(round(a), round(b)) for a, b in points]))

    def dot(a, b, w, h, color):
        p.fillRect(round(a), round(b), w, h, color)

    def gills(a, b, direction):
        flutter = pet.idle_frame * 2 + (1 if pet.ear_twitch else 0)
        for dy in (-13, 0, 13):
            tip = b + dy + (flutter if dy > 0 else -flutter)
            shape([(a, b+dy//3), (a+direction*13, tip-5),
                   (a+direction*19, tip-5), (a+direction*19, tip+1),
                   (a+direction*12, tip+5), (a, b+dy//3+4)], c['gill'])
            line([(a+direction*4, b+dy//3+1), (a+direction*15, tip)], c['fin'], 2)
            dot(a+direction*14-1, tip-6, 3, 4, c['gill'])

    def eye(a, b):
        if asleep or state in ('blink', 'happy'):
            line([(a, b+1), (a+3, b+3), (a+7, b+1)], c['eye'])
        else:
            dot(a, b, 6, 7, c['eye'])
            dot(a+1, b, 2, 2, QColor('#FFFFFF'))

    if asleep:
        breath = round((1-math.cos(pet.breath_phase))*.7)
        shape([(28,72),(33,59-breath),(51,53-breath),(73,56-breath),
               (85,66),(89,77),(76,84),(36,84)], c['body'])
        shape([(76,64),(95,59),(106,64),(109,74),(101,82),(81,85),(60,81),
               (72,74),(92,75),(94,70)], c['fin'])
        line([(76,78),(95,78),(102,72)], c['gill'])
        p.save()
        p.translate(0, round(pet.sleep_progress*3) if state=='drowsy' else 3)
        gills(29,59,-1)
        shape([(25,52),(34,47),(50,48),(61,56),(61,70),(51,78),(29,77),(20,68),(20,59)],c['body'])
        eye(28,61)
        eye(47,62)
        line([(36,70),(39,72),(43,70)],c['outline'],1)
        dot(24,69,6,3,c['gill'])
        p.restore()
        if state=='sleeping':
            for a,b in ((76,35),(88,24)):
                line([(a,b),(a+5,b),(a,b+5),(a+5,b+5)],QColor('#DDE6F5'),1)
        p.restore()
        return

    if state == 'walking':
        p.translate(0, -(0,1,2,1,0,1,2,1)[phase])
    elif state in ('climbing','slipping'):
        p.translate(70,65)
        p.rotate(-32 if state=='climbing' else -12)
        p.translate(-70,-65)
    elif state == 'held':
        p.translate(56,53)
        p.rotate(5 if pet.idle_frame else -5)
        p.translate(-56,-53)
    elif state in ('stretch','settle','landing'):
        p.translate(0,84)
        p.scale(.96 if state=='stretch' else 1.04,1.1 if state=='stretch' else .9)
        p.translate(0,-84)

    if side:
        shape([(43,65),(28,57+sway),(14,48+sway),(6,48+sway),(8,66+sway),
               (21,76),(43,78)],c['fin'])
        line([(12,57+sway),(27,68),(42,71)],c['gill'])
        stride=(0,3,5,3,0,-3,-5,-3)[phase]
        for a, step in ((42,-stride),(77,stride)):
            shape([(a,70),(a+8,70),(a+9+step,81),(a+5+step,84),
                   (a-3+step,84),(a-4+step,80)],c['body'])
        shape([(30,65),(40,53),(59,49),(78,54),(85,66),(79,77),(44,78)],c['body'])
        shape([(42,69),(60,64),(77,65),(73,74),(47,75)],c['patch'],False)
        gills(69,43,-1)
        shape([(69,35),(79,30),(94,32),(104,41),(107,54),(101,65),
               (83,68),(70,60),(65,48)],c['body'])
        eye(92,44)
        dot(94,55,7,3,c['gill'])
        line([(100,57),(104,56)],c['outline'],1)
        shape([(65,67),(70,64),(76+stride,77),(72+stride,83),(65+stride,82)],c['body'])
    else:
        shape([(70,72),(84,65+sway),(99,50+sway),(105,50+sway),
               (106,66+sway),(98,78),(82,84),(66,82)],c['fin'])
        line([(77,78),(92,71),(101,58+sway)],c['gill'])
        shape([(34,62),(41,51),(66,51),(76,63),(78,76),(69,83),(39,83),(30,75)],c['body'])
        shape([(43,60),(61,58),(69,67),(65,77),(45,79),(38,71)],c['patch'],False)
        for a in (31,64):
            end=89 if state=='held' else 84
            shape([(a+2,72),(a+11,72),(a+14,end-3),(a+9,end),(a-2,end),(a-4,end-4)],c['body'])
            for toe in (0,4,8):
                dot(a+toe,end-2,1,2,c['gill'])
        p.save()
        if state in ('curious','look'):
            p.translate(pet.curious_direction*2, -pet.idle_frame)
        elif state=='sniff':
            p.translate(0,pet.idle_frame*2)
        gills(29,39,-1)
        gills(80,39,1)
        shape([(26,32),(34,23),(47,20),(65,20),(77,25),(85,34),(87,46),
               (82,57),(71,63),(39,63),(27,56),(22,45)],c['body'])
        shape([(34,28),(45,24),(63,24),(70,27),(42,29)],c['patch'],False)
        eye(36,40)
        eye(68,40)
        dot(29,50,9,4,c['gill'])
        dot(74,50,9,4,c['gill'])
        line([(49,51),(52,54),(56,54),(60,51)],c['outline'],2)
        if state=='happy':
            dot(53,54,4,3,c['gill'])
        if state=='angry':
            line([(34,36),(43,39)],c['outline'])
            line([(67,39),(76,36)],c['outline'])
        p.restore()
        for a in (34,70):
            raised=state=='groom' and a==34
            hand=51-pet.idle_frame*2 if raised else 74
            shape([(a,62),(a+6,62),(a+7,hand),(a+2,hand+3),(a-2,hand)],c['body'])
    if state=='happy':
        shape([(91,19),(94,16),(97,19),(100,16),(103,19),(103,23),(97,29),(91,23)],c['gill'],False)
    p.restore()
