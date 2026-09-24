"""Golden Shiba pixel art inspired by Doge's cheeks and sideways glance."""
import math
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPainter, QPen, QPolygon


def draw_dog(pet,p,x,y):
    c=pet.pets[pet.skin]['colors']
    vested = 'vest' in c
    state=pet.state
    phase=pet.walk_phase % 8
    side=state in ('walking','wall_look','climbing','slipping','landing')
    sleeping=state in ('sleeping','drowsy')
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

    def block(a,b,w,h,color):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawRect(round(a),round(b),w,h)

    def curl(a,b):
        points=[(a,b),(a+13,b-2),(a+21,b-12),(a+18,b-24),(a+8,b-28),(a,b-22),(a+1,b-14),(a+9,b-12),(a+13,b-17)]
        line(points,c['outline'],11)
        line(points,c['body'],7)
        line([(a+1,b-21),(a+2,b-16),(a+9,b-15)],c['patch'],3)

    def eyes(a,b,closed=False,angry=False):
        if closed:
            line([(a,b+3),(a+3,b+5),(a+8,b+3)],c['eye'],2)
        else:
            shape([(a,b+1),(a+5,b),(a+9,b+2),(a+8,b+7),(a+2,b+7)],QColor('#FFF8DF'),False)
            shift=2 if state!='curious' else pet.curious_direction+2
            block(a+shift,b+1,4,6,c['eye'])
            block(a+shift,b+1,1,2,QColor('#FFFFFF'))
        if angry:
            line([(a-1,b-2),(a+8,b+1)],c['outline'],2)
        else:
            line([(a-1,b-3),(a+4,b-5),(a+8,b-4)],c['shade'],2)

    if sleeping:
        breath=round((1-math.cos(pet.breath_phase))*.75)
        drop=round((1 if state=='sleeping' else pet.sleep_progress)*10)
        shape([(25,65),(31,51-breath),(49,42-breath),(73,44-breath),(91,54-breath),
               (96,71),(88,81),(40,82),(24,75)],c['body'])
        if vested:
            shape([(43,46-breath),(59,43-breath),(75,46-breath),(89,55-breath),
                   (93,68),(85,77),(59,78),(46,69)],c['vest'])
            shape([(77,51-breath),(87,57-breath),(90,67),(82,73),(76,69)],c['vest_shadow'],False)
            line([(53,49-breath),(70,51-breath),(82,59-breath)],c['vest_light'],2)
            line([(58,72),(79,73)],c['vest_shadow'],2)
            block(70,61,8,5,c['patch'])
        shape([(27,74),(40,71),(52,75),(53,81),(23,81)],c['patch'])
        shape([(22,47+drop),(20,30+drop),(26,31+drop),(35,41+drop),
               (44,38+drop),(54,29+drop),(58,47+drop),(58,59+drop),
               (46,68+drop),(29,67+drop),(18,58+drop)],c['body'])
        shape([(21,53+drop),(32,55+drop),(38,59+drop),(46,54+drop),(55,53+drop),
               (51,63+drop),(39,66+drop),(26,61+drop)],c['patch'],False)
        eyes(24,48+drop,True)
        eyes(43,48+drop,True)
        shape([(34,59+drop),(41,59+drop),(38,63+drop)],c['outline'],False)
        curl(76,76)
        if state=='sleeping':
            for a,b,k in [(76,28,4),(88,19,5)]:
                line([(a,b),(a+k,b),(a,b+k),(a+k,b+k)],QColor('#D8DDEA'),1)
        p.restore()
        return

    if side:
        stride=round(math.sin(phase*math.pi/4)*(9 if pet.running else 5))
        bob=(0,-1,-3,-1,0,-1,-3,-1)[phase] if state=='walking' else 0
        if state in ('climbing','slipping'):
            p.translate(65,65)
            p.rotate(-35 if state=='climbing' else -12)
            p.translate(-65,-65)
        if state=='landing':
            p.translate(0,84)
            p.scale(1,.85)
            p.translate(0,-84)
        # Curl mirrored to sit behind the back.
        p.save()
        p.translate(50,0)
        p.scale(-1,1)
        curl(13,62+bob)
        p.restore()
        for a,offset in ((37,-stride),(73,stride)):
            shape([(a,63),(a+8,63),(a+offset+9,81),(a+offset-1,83)],c['shade'])
        shape([(28,52+bob),(38,43+bob),(66,42+bob),(82,50+bob),
               (84,66+bob),(73,76),(40,75),(28,66)],c['body'])
        shape([(46,61+bob),(77,55+bob),(79,68),(73,73),(50,73)],c['patch'],False)
        if vested:
            shape([(37,45+bob),(66,44+bob),(80,51+bob),(79,59+bob),
                   (71,62+bob),(68,72),(42,73),(35,65)],c['vest'])
            shape([(38,46+bob),(44,47+bob),(45,70),(39,68),(35,63)],c['vest_shadow'],False)
            line([(45,47+bob),(63,46+bob),(73,50+bob)],c['vest_light'],2)
            line([(73,54+bob),(70,60+bob),(70,68)],c['vest_shadow'],2)
            block(53,54+bob,10,7,c['vest_shadow'])
            block(54,54+bob,8,2,c['vest_light'])
            line([(45,71),(65,70)],c['outline'],1)
        for a,offset in ((34,stride),(74,-stride)):
            shape([(a,67+bob),(a+7,67+bob),(a+offset+7,78),(a+offset+11,81),
                   (a+offset+10,84),(a+offset-2,84),(a-1,73)],c['body'])
            line([(a+offset+1,81),(a+offset+7,81)],c['patch'],3)
        shape([(65,35+bob),(65,17+bob),(72,12+bob),(80,28+bob),
               (89,27+bob),(95,35+bob),(96,44+bob),(101,48+bob),
               (100,57+bob),(89,63+bob),(74,59+bob),(64,50+bob)],c['body'])
        shape([(69,27+bob),(70,19+bob),(76,29+bob)],c['ear'],False)
        shape([(78,45+bob),(89,43+bob),(94,48+bob),(100,50+bob),
               (98,56+bob),(87,58+bob),(77,53+bob)],c['patch'],False)
        eyes(85,36+bob,state=='wall_look')
        block(98,48+bob,5,4,c['outline'])
        line([(92,56+bob),(99,55+bob)],c['outline'],1)
        p.restore()
        return

    b=pet.idle_frame
    # Three-quarter portrait: a substantial seated chest and crossed forepaws.
    # Keep the tail behind the flank rather than competing with the face.
    line([(84,75),(94,72),(97,65),(93,59)],c['outline'],7)
    line([(84,75),(94,72),(97,65),(93,59)],c['body'],4)
    shape([(36,38),(59,33),(76,36),(87,45),(91,60),(89,75),
           (80,83),(40,83),(28,76),(26,65),(31,50)],c['body'])
    shape([(37,44),(51,40),(69,45),(78,56),(77,70),(69,79),
           (43,78),(32,69),(33,57)],c['patch'],False)
    shape([(77,43),(85,48),(87,64),(82,75),(75,75),(78,61)],c['shade'],False)
    line([(45,53),(50,55),(56,54)],QColor('#E7C790'),2)
    line([(40,61),(44,63),(50,62)],QColor('#E7C790'),2)
    if vested:
        # Sleeveless panels sit behind the forelegs and underneath the neck.
        shape([(34,45),(44,40),(52,47),(59,47),(69,40),(83,46),
               (87,58),(83,75),(72,81),(43,81),(31,73),(30,59)],c['vest'])
        shape([(77,47),(84,51),(84,64),(79,75),(74,76),(77,61)],c['vest_shadow'],False)
        shape([(40,45),(48,47),(54,55),(48,59),(38,52)],c['vest_light'],False)
        shape([(65,45),(73,44),(75,51),(60,60),(54,55)],c['vest_light'],False)
        line([(54,54),(56,73),(58,80)],c['outline'],2)
        line([(55,56),(57,71)],QColor('#FFE0A2'),1)
        block(53,59,5,4,QColor('#E3D3BD'))
        shape([(64,63),(73,61),(75,69),(66,71)],c['vest_shadow'],False)
        line([(65,63),(72,62)],c['vest_light'],2)
        line([(36,74),(46,78)],c['vest_shadow'],2)
    # One foreleg lies diagonally over the other, as in the reference photograph.
    if state=='held':
        for ax in (40,66):
            shape([(ax,66),(ax+10,66),(ax+11,86),(ax+7,89),(ax-1,87)],c['body'])
            line([(ax+2,85),(ax+8,85)],c['patch'],3)
    else:
        shape([(35,62),(42,64),(48,72),(65,77),(71,82),(64,85),
               (48,81),(33,76),(28,71)],c['body'])
        shape([(77,63),(82,68),(79,75),(69,81),(59,84),(49,83),
               (45,79),(49,74),(61,73),(69,67)],c['patch'])
        for ax,ay in ((52,78),(57,80),(62,80)):
            line([(ax,ay),(ax-1,ay+3)],c['shade'],1)
    p.save()
    p.translate(55,39)
    p.rotate(pet.curious_direction*4 if state=='curious' else -4)
    p.translate(-55,-39)
    # Ears have unequal apparent widths in a three-quarter view.
    shape([(37,20),(38,5),(42,1),(47,5),(53,17)],c['body'])
    shape([(64,17),(76,3),(81,3),(85,10),(83,27)],c['body'])
    shape([(41,16),(42,7),(48,17)],c['shade'],False)
    shape([(72,18),(79,8),(81,12),(80,22)],c['shade'],False)
    shape([(34,19),(46,13),(63,13),(76,18),(83,27),(84,37),
           (77,47),(65,53),(49,54),(35,49),(28,40),(28,29)],c['body'])
    # Cream blends along the cheek and lower jaw; there is no central cat muzzle.
    shape([(31,29),(37,27),(43,31),(49,38),(59,39),(70,34),(80,31),
           (80,40),(70,47),(56,51),(43,49),(32,43),(29,37)],c['patch'],False)
    shape([(45,18),(51,17),(48,25),(42,30),(37,31)],QColor('#EAC68B'),False)
    closed=state in ('blink','happy','groom','stretch')

    def doge_eye(ax,ay,wide):
        if closed:
            line([(ax,ay+3),(ax+3,ay+5),(ax+wide,ay+3)],c['eye'],2)
        else:
            shape([(ax,ay+2),(ax+3,ay),(ax+wide-2,ay),(ax+wide,ay+3),
                   (ax+wide-1,ay+7),(ax+3,ay+8),(ax-1,ay+5)],c['outline'],False)
            block(ax+2,ay+1,wide-3,6,QColor('#F3E4C7'))
            shift=0 if state!='curious' else pet.curious_direction
            block(ax+1+shift,ay+1,5,6,c['eye'])
            block(ax+2+shift,ay+1,2,2,QColor('#FFFDF5'))
        line([(ax,ay-3),(ax+3,ay-5),(ax+wide-1,ay-3)],c['shade'],2)
    doge_eye(37,23,8)
    doge_eye(58,26,11)
    # Nose projects to the left; its wide dark top and offset mouth carry the likeness.
    shape([(31,36),(35,32),(43,32),(48,36),(46,41),(39,43),(32,41)],c['outline'],False)
    line([(35,34),(41,34)],QColor('#69604E'),2)
    line([(39,43),(40,46),(48,48),(57,47),(62,44)],c['outline'],2)
    line([(34,46),(40,46)],c['outline'],1)
    if state=='happy':
        shape([(44,48),(51,49),(51,52),(47,54),(44,52)],c['ear'],False)
    if state=='angry':
        line([(35,22),(46,25)],c['outline'],2)
        line([(58,24),(69,25)],c['outline'],2)
    p.restore()
    if state=='groom':
        shape([(36,71),(31,48-b*3),(35,44-b*3),(43,47-b*3),(46,65)],c['body'])
    if state=='angry':
        line([(89,21),(94,21),(94,16)],QColor('#F07868'),2)
        line([(99,16),(99,21),(104,21)],QColor('#F07868'),2)
    p.restore()
