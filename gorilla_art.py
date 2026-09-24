"""Pixel gorilla art with broad shoulders, heavy knuckles and a soft face."""
import math
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QPen, QPolygon, QColor


def draw_gorilla(pet, p, x, y):
    c=pet.pets[pet.skin]['colors']
    state=pet.state
    phase=pet.walk_phase % 8
    sleeping=state in ('sleeping','drowsy')
    wall=state in ('climbing','slipping')
    side=state in ('walking','wall_look','landing') or wall
    p.save()
    p.translate(x,y)
    p.setRenderHint(QPainter.Antialiasing,False)
    if side and pet.facing < 0:
        p.translate(114,0)
        p.scale(-1,1)

    def shape(points,color,border=True):
        p.setPen(QPen(c['outline'],3,Qt.SolidLine,Qt.SquareCap,Qt.MiterJoin) if border else Qt.NoPen)
        p.setBrush(color)
        p.drawPolygon(QPolygon([QPoint(round(a),round(b)) for a,b in points]))

    def line(points,color,width=2):
        p.setPen(QPen(color,width,Qt.SolidLine,Qt.SquareCap,Qt.MiterJoin))
        p.drawPolyline(QPolygon([QPoint(round(a),round(b)) for a,b in points]))

    def block(a,b,w,h,color):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawRect(round(a),round(b),w,h)

    def fist(a,b):
        shape([(a,b+3),(a+4,b),(a+13,b),(a+17,b+4),(a+16,b+12),(a+2,b+12),(a,b+9)],c['face'])
        for dx in (5,10):
            line([(a+dx,b+7),(a+dx,b+11)],c['outline'],1)

    def eyes(a,b,closed=False):
        if closed:
            line([(a,b+2),(a+3,b+4),(a+7,b+2)],c['eye'],2)
        else:
            block(a+1,b,5,7,c['eye'])
            block(a+2,b,2,2,QColor('#FFF6E7'))

    if sleeping:
        t=1 if state=='sleeping' else pet.sleep_progress
        breath=round((1-math.cos(pet.breath_phase))*.75)
        shape([(25,68),(30,51-breath),(44,42-breath),(65,40-breath),(83,47-breath),
               (94,64),(93,77),(82,83),(35,83)],c['body'])
        shape([(54,48-breath),(70,46-breath),(84,53-breath),(87,63),(78,68),(59,64)],c['highlight'],False)
        # Huge forearm becomes a pillow for the cheek.
        shape([(29,68),(47,66),(67,72),(72,79),(66,83),(25,83),(19,77)],c['body'])
        fist(66,71)
        drop=round(t*7)
        shape([(20,49+drop),(25,38+drop),(39,34+drop),(53,38+drop),(61,47+drop),
               (58,63+drop),(45,72+drop),(28,68+drop)],c['body'])
        shape([(24,48+drop),(32,43+drop),(47,45+drop),(55,53+drop),(51,65+drop),
               (34,67+drop),(24,60+drop)],c['face'])
        eyes(29,50+drop,True)
        eyes(44,52+drop,True)
        block(36,58+drop,8,4,c['outline'])
        if state=='sleeping':
            rise=round(pet.breath_phase/(2*math.pi)%1*4)
            for a,b,k in [(73,29-rise,4),(84,19-rise,6)]:
                line([(a,b),(a+k,b),(a,b+k),(a+k,b+k)],QColor('#D8DDEA'),1)
        p.restore()
        return

    if side:
        stride=(0,3,6,3,0,-3,-6,-3)[phase] if state=='walking' or wall else 0
        bob=(0,-1,-3,-1,0,-1,-3,-1)[phase] if state=='walking' else 0
        if state=='landing':
            p.translate(0,84)
            p.scale(1,.86)
            p.translate(0,-84)
        if wall:
            p.translate(64,64)
            p.rotate(-33 if state=='climbing' else -12)
            p.translate(-64,-64)
        # Rear bent legs and a high silverback shoulder ridge.
        shape([(35,58+bob),(47,59+bob),(49,71),(45-stride,81),
               (29-stride,82),(27-stride,78),(36,70)],c['body'])
        shape([(29,55+bob),(37,39+bob),(54,32+bob),(71,34+bob),
               (82,46+bob),(76,63+bob),(61,71),(39,70),(29,64)],c['body'])
        shape([(35,46+bob),(48,36+bob),(63,35+bob),(72,40+bob),(67,48+bob),
               (54,47+bob),(43,54+bob)],c['highlight'],False)
        shape([(59,45+bob),(72,43+bob),(81,51+bob),(78,66+bob),
               (83+stride,73),(82+stride,81),(67+stride,81),(65,68)],c['body'])
        line([(67,50+bob),(73,54+bob),(70,62+bob)],c['highlight'],3)
        fist(68+stride,71)
        # Brow, muzzle and small ear make the side face recognizable.
        shape([(65,29+bob),(74,23+bob),(87,25+bob),(94,35+bob),
               (94,42+bob),(97,47+bob),(96,56+bob),(87,60+bob),
               (74,55+bob),(66,43+bob)],c['body'])
        shape([(79,34+bob),(91,35+bob),(92,43+bob),(96,47+bob),
               (94,55+bob),(85,57+bob),(77,48+bob)],c['face'])
        shape([(66,37+bob),(70,34+bob),(75,37+bob),(74,44+bob),(68,45+bob)],c['face'])
        eyes(84,38+bob,state=='wall_look')
        line([(80,35+bob),(91,35+bob)],c['outline'],3)
        shape([(90,43+bob),(95,44+bob),(97,48+bob),(91,49+bob)],c['outline'],False)
        line([(85,54+bob),(94,54+bob)],c['outline'],2)
        p.restore()
        return

    b=pet.idle_frame
    if state=='angry':
        p.translate(0,-b)
    elif state=='stretch':
        p.translate(0,-2)
    # A wide inverted-triangle torso, pecs and abdominal highlights.
    shape([(27,47),(36,35),(51,32),(69,34),(82,45),(77,64),
           (68,77),(42,77),(31,64)],c['body'])
    shape([(35,46),(49,40),(54,43),(52,55),(40,56),(34,51)],c['highlight'],False)
    shape([(58,43),(64,40),(76,46),(77,52),(68,56),(57,55)],c['highlight'],False)
    shape([(45,59),(65,59),(64,70),(57,75),(47,71)],c['face'],False)
    line([(54,59),(54,70)],c['body'],2)
    line([(47,65),(63,65)],c['body'],2)
    for a in (36,60):
        extra=5 if state=='held' else 0
        shape([(a,70),(a+12,70),(a+15,80+extra),(a+10,84+extra),
               (a-3,84+extra),(a-5,80+extra)],c['body'])
        line([(a,81+extra),(a+9,81+extra)],c['face'],3)
    # Deltoids and biceps with broad forearms; happy gorillas flex.
    flex=state in ('happy','stretch')
    for mirrored in (False,True):
        p.save()
        if mirrored:
            p.translate(110,0)
            p.scale(-1,1)
        if flex:
            shape([(33,43),(23,40),(16,32),(15,22),(23,17),(31,22),
                   (29,32),(38,35)],c['body'])
            fist(13,12)
            line([(22,31),(24,37),(31,40)],c['highlight'],3)
        else:
            shape([(31,39),(22,41),(16,51),(15,66),(12,73),
                   (18,81),(29,80),(32,65),(40,49)],c['body'])
            line([(25,46),(22,51),(23,59)],c['highlight'],4)
            fist(12,70)
        p.restore()
    p.save()
    if state=='curious':
        p.translate(pet.curious_direction*2,0)
    # Compact cute face framed by a heavy brow; no tail or pointed animal ears.
    shape([(33,26),(35,15),(43,9),(59,7),(71,14),(77,26),
           (75,40),(66,48),(45,48),(35,39)],c['body'])
    for a in (30,73):
        shape([(a,27),(a+3,25),(a+6,27),(a+6,32),(a+2,34),(a,31)],c['body'])
        line([(a+2,28),(a+3,31)],c['face'],2)
    shape([(37,25),(45,20),(53,23),(58,23),(66,20),(73,26),
           (72,39),(64,44),(47,44),(38,38)],c['face'])
    closed=state in ('blink','happy','groom','stretch')
    eyes(41,26,closed)
    eyes(61,26,closed)
    # Connected brow ridge and a flat dark nose, without a round snout outline.
    line([(39,24),(47,23),(53,26),(58,26),(64,23),(71,24)],c['outline'],3)
    shape([(46,35),(50,31),(59,31),(64,35),(61,39),(49,39)],c['outline'],False)
    line([(51,33),(58,33)],c['body'],1)
    shape([(43,39),(48,40),(62,40),(67,38),(65,44),(60,47),(49,47),(44,44)],c['face'],False)
    if state=='happy':
        line([(48,42),(53,44),(59,44),(63,42)],c['outline'],2)
    elif state=='held':
        block(53,41,5,4,c['outline'])
    else:
        line([(48,43),(62,43)],c['outline'],2)
    line([(39,35),(42,38)],c['body'],2)
    line([(69,35),(66,38)],c['body'],2)
    p.restore()
    if state=='groom':
        fist(31,32-b*3)
    if state=='angry':
        line([(88,21),(93,21),(93,16)],QColor('#F07868'),2)
        line([(98,16),(98,21),(103,21)],QColor('#F07868'),2)
    p.restore()
