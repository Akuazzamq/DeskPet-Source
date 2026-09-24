"""Chunky pixel dragons; Emerald wings and a red/gold lunar dragon variant."""
import math
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPainter, QPen, QPolygon


def draw_dragon(pet,p,x,y):
    c=pet.pets[pet.skin]['colors']
    red=pet.skin=='red_dragon'
    state=pet.state
    phase=pet.walk_phase % 8
    flying=state=='walking'
    sleeping=state in ('sleeping','drowsy')
    wall=state in ('climbing','slipping')
    side=flying or wall or state in ('wall_look','landing')
    p.save()
    p.translate(x,y)
    p.setRenderHint(QPainter.Antialiasing,False)
    if side and pet.facing<0:
        p.translate(114,0)
        p.scale(-1,1)

    def shape(points,color,border=True):
        p.setPen(QPen(c['outline'],3,Qt.SolidLine,Qt.SquareCap,Qt.MiterJoin) if border else Qt.NoPen)
        p.setBrush(color)
        p.drawPolygon(QPolygon([QPoint(round(a),round(b)) for a,b in points]))

    def line(points,color,width=2):
        p.setPen(QPen(color,width,Qt.SolidLine,Qt.SquareCap,Qt.MiterJoin))
        p.drawPolyline(QPolygon([QPoint(round(a),round(b)) for a,b in points]))

    def dot(a,b,w,h,color):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawRect(round(a),round(b),w,h)

    def horn(a,b,flip=1):
        # Broad root tapering to a swept point, still contained in the sprite.
        shape([(a-3,b),(a+flip*5,b-7),(a+flip*8,b-17),
               (a+flip*2,b-13),(a-flip*2,b-7)],c['gold'])
        if red:
            line([(a+flip*4,b-7),(a+flip*12,b-10),(a+flip*15,b-15)],c['gold'],3)

    def eye(a,b,closed=False,flip=False):
        if closed:
            line([(a,b+3),(a+4,b+5),(a+8,b+3)],c['eye'],2)
        else:
            points=[(a,b+1),(a+9,b+4),(a+8,b+8),(a+2,b+7)]
            if flip:
                points=[(a,b+4),(a+9,b+1),(a+8,b+7),(a+1,b+8)]
            shape(points,c['eye'],False)
            dot(a+4,b+3,2,5,c['outline'])
            dot(a+2,b+3,1,1,QColor('#FFF8DC'))
            line([(a-1,b),(a+10,b+3)] if not flip else [(a-1,b+3),(a+10,b)],c['outline'],3)

    def whisker(a,b,flip=1):
        line([(a,b),(a+flip*8,b+2),(a+flip*14,b-3),(a+flip*15,b-8)],c['gold'],2)

    if sleeping:
        breath=round((1-math.cos(pet.breath_phase))*.75)
        drop=round((1 if state=='sleeping' else pet.sleep_progress)*7)
        shape([(25,70),(29,54-breath),(44,44-breath),(65,42-breath),(82,49-breath),
               (93,65),(91,77),(77,83),(37,83)],c['body'])
        for a in (54,66,78):
            shape([(a,47-breath),(a+3,39-breath),(a+8,47-breath)],c['gold'])
        if not red:
            shape([(67,52),(81,52),(84,69),(75,63),(68,68),(62,57)],c['wing'])
            line([(68,54),(76,63)],c['gold'],1)
        horn(30,46+drop,-1)
        horn(49,46+drop)
        shape([(21,48+drop),(34,40+drop),(48,42+drop),(57,53+drop),(56,64+drop),
               (44,73+drop),(28,71+drop),(18,61+drop)],c['body'])
        shape([(22,61+drop),(34,58+drop),(49,62+drop),(49,70+drop),(30,72+drop)],c['belly'],False)
        eye(25,51+drop,True)
        eye(43,53+drop,True)
        dot(30,63+drop,3,2,c['outline'])
        if red:
            whisker(24,65+drop,-1)
        shape([(85,62),(98,65),(102,74),(94,82),(76,84),(58,81),(54,76),
               (66,73),(82,75),(90,72)],c['body'])
        shape([(55,76),(60,70),(64,75),(70,76),(65,80)],c['gold'],False)
        if state=='sleeping':
            for a,b,k in [(79,28,4),(91,18,5)]:
                line([(a,b),(a+k,b),(a,b+k),(a+k,b+k)],QColor('#D8DDEA'),1)
        p.restore()
        return

    if side:
        # Shadow stays on the floor while tucked feet float above it.
        lift=(6,8,11,13,12,10,7,5)[phase] if flying else 0
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0,0,0,35))
        p.drawEllipse(30+lift//2,81,65-lift,4)
        p.translate(0,-lift)
        if wall:
            p.translate(66,63)
            p.rotate(-30 if state=='climbing' else -10)
            p.translate(-66,-63)
        if state=='landing':
            p.translate(0,84)
            p.scale(1,.84)
            p.translate(0,-84)
        sway=(0,2,3,2,0,-2,-3,-2)[phase]
        shape([(41,66),(26,67+sway),(15,60+sway),(7,48+sway),(5,59+sway),
               (15,75+sway),(29,81),(45,77)],c['body'])
        shape([(6,50+sway),(11,46+sway),(13,55+sway),(9,59+sway)],c['gold'],False)
        shape([(34,61),(43,45),(59,39),(75,45),(83,59),(80,72),(66,81),(44,78)],c['body'])
        shape([(64,50),(77,53),(79,68),(68,76),(56,76),(62,64)],c['belly'],False)
        for a in (39,48,57):
            shape([(a,48),(a+1,38),(a+8,45)],c['gold'])
        shape([(46,70),(52,68),(60,78),(56,83),(44,82)],c['body'])
        shape([(70,64),(76,63),(84,70),(83,76),(76,76)],c['body'])
        if not red:
            flap=(-12,-6,4,13,17,8,-3,-10)[phase]
            shape([(55,57),(39,25+flap),(16,20+flap),(19,40+flap),(28,36+flap),
                   (32,53+flap),(41,45+flap),(47,59+flap)],c['wing'])
            line([(51,54),(36,33+flap),(27,29+flap)],c['gold'],2)
        else:
            shape([(63,38),(59,30),(69,33),(70,27),(76,33),(83,30),(82,40)],c['gold'])
        horn(76,34,-1)
        horn(88,34)
        shape([(65,37),(72,29),(86,29),(96,38),(97,45),(108,48),
               (109,59),(99,66),(79,63),(66,51)],c['body'])
        shape([(85,47),(95,47),(105,50),(102,58),(89,59)],c['belly'],False)
        eye(84,37,state=='wall_look')
        dot(102,51,3,2,c['outline'])
        line([(90,57),(105,57)],c['outline'],2)
        shape([(96,57),(99,63),(102,57)],QColor('#FFF5DA'),False)
        if red:
            whisker(100,58,-1)
            line([(90,63),(93,69),(97,66)],c['gold'],2)
        p.restore()
        return

    b=pet.idle_frame
    shape([(72,74),(86,71),(96,61),(98,50),(104,58),(102,71),(92,81),(74,82)],c['body'])
    shape([(97,53),(102,46),(107,54),(104,61)],c['gold'])
    # Small wings frame a broad chest; the red variant has a golden mane instead.
    for flip in (False,True):
        p.save()
        if flip:
            p.translate(110,0)
            p.scale(-1,1)
        if not red:
            shape([(39,62),(30,36),(12,25),(8,31),(10,50),(18,43),(23,62),(30,53),(34,66)],c['wing'])
            line([(34,56),(23,44),(17,42)],c['gold'],1)
        else:
            shape([(36,43),(21,30),(23,42),(12,40),(20,52),(13,56),(27,61),(22,68),(39,59)],c['gold'])
        p.restore()
    shape([(33,71),(37,52),(45,44),(64,44),(74,55),(79,73),(72,82),(39,82)],c['body'])
    shape([(46,50),(62,49),(69,61),(65,76),(53,81),(42,74),(40,61)],c['belly'],False)
    for ay in (58,65,72):
        line([(44,ay),(64,ay)],c['gold'].darker(125),1)
    for a in (33,64):
        end=88 if state=='held' else 83
        shape([(a+2,72),(a+11,72),(a+15,end-4),(a+10,end),(a-3,end),(a-4,end-4)],c['body'])
        for claw in (0,5,10):
            dot(a+claw,end-2,2,2,c['gold'])
    p.save()
    if state=='curious':
        p.translate(pet.curious_direction*2,0)
    horn(36,24,-1)
    horn(72,24)
    shape([(23,29),(34,18),(48,16),(68,18),(82,28),(87,38),(83,47),
           (86,54),(73,61),(63,66),(42,65),(30,58),(21,52),(25,45),(20,37)],c['body'])
    if red:
        shape([(42,20),(43,8),(51,14),(57,5),(61,14),(68,8),(69,21)],c['gold'])
        line([(32,27),(42,25)],c['gold'],3)
        line([(64,25),(75,27)],c['gold'],3)
    closed=state in ('blink','happy','groom','stretch')
    eye(34,32,closed)
    eye(64,32,closed,True)
    shape([(33,47),(45,42),(65,43),(77,49),(77,55),(66,61),(48,62),(34,56)],c['belly'],False)
    dot(46,48,3,2,c['outline'])
    dot(61,48,3,2,c['outline'])
    line([(36,54),(46,57),(63,57),(74,53)],c['outline'],2)
    shape([(38,55),(42,61),(45,56)],QColor('#FFF5DA'),False)
    shape([(65,56),(68,61),(72,55)],QColor('#FFF5DA'),False)
    if state=='happy':
        dot(51,58,5,3,c['blush'])
    if red:
        whisker(36,51,-1)
        whisker(74,51)
        shape([(49,61),(54,68),(59,61)],c['gold'],False)
    else:
        shape([(27,31),(22,23),(34,26)],c['gold'])
        shape([(74,26),(86,23),(81,32)],c['gold'])
    p.restore()
    if state=='groom':
        shape([(36,72),(32,51-b*3),(38,48-b*3),(43,53-b*3),(45,66)],c['body'])
    if state=='angry':
        line([(85,20),(90,20),(90,15)],QColor('#F07868'),2)
        line([(95,15),(95,20),(100,20)],QColor('#F07868'),2)
    p.restore()
