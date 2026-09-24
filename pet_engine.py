import math
from special_actions import draw_special

from rabbit_art import draw_rabbit
from gorilla_art import draw_gorilla
from dog_art import draw_dog
from dragon_art import draw_dragon
from axolotl_art import draw_axolotl
from panda_art import draw_panda
from duck_art import draw_duck
from penguin_art import draw_penguin

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QPolygon


class PetEngine:
    def __init__(self):
        self.special_progress = 0.0
        self.taskbar_effects = False
        self.effect_phase = 0.0
        self.state = "idle"
        self.skin = "cream_cat"

        # Animation frames
        self.facing = 1
        self.animation_phase = 0
        self.walk_phase = 0
        self.running = False
        self.wall_height = 0
        self.sleep_progress = 0.0
        self.breath_phase = 0.0
        self.tail_frame = 0
        self.idle_frame = 0
        self.ear_twitch = False

        # Curious
        self.curious_direction = 0

        self.pets = {
            "cream_cat": {
                "type": "cat",
                "name": "Cream Cat",
                "colors": {
                    "body": QColor("#FFF1DC"),
                    "patch": QColor("#BFA89A"),
                    "outline": QColor("#332B30"),
                    "ear": QColor("#F7A6A6"),
                    "eye": QColor("#30292E"),
                    "blush": QColor("#F3A0A0"),
                },
            },

            "orange_cat": {
                "type": "cat",
                "name": "Orange Cat",
                "colors": {
                    "body": QColor("#F5A24B"),
                    "patch": QColor("#FFF0D5"),
                    "outline": QColor("#3A2924"),
                    "ear": QColor("#F7A0A0"),
                    "eye": QColor("#30292E"),
                    "blush": QColor("#F28E8E"),
                },
            },

            "black_cat": {
                "type": "cat",
                "name": "Black Cat",
                "colors": {
                    "body": QColor("#45414D"),
                    "patch": QColor("#595362"),
                    "outline": QColor("#211E24"),
                    "ear": QColor("#D77C91"),
                    "eye": QColor("#F0D66D"),
                    "blush": QColor("#C66B7D"),
                },
            },

            "orange_fox": {
                "type": "fox",
                "name": "Orange Fox",
                "colors": {
                    "body": QColor("#E98235"),
                    "patch": QColor("#FFF0D6"),
                    "outline": QColor("#352825"),
                    "ear": QColor("#E88F82"),
                    "eye": QColor("#302725"),
                    "blush": QColor("#F2A09B"),
                    "stripe": QColor("#B95628"),
                    "tail_tip": QColor("#FFF7EA"),
                },
            },
        }

        for skin, name, body, patch, outline in (
            ('snow_rabbit', 'Snow Rabbit', '#F5F1EB', '#E3DDD6', '#45404D'),
            ('caramel_rabbit', 'Caramel Rabbit', '#C78F5D', '#F4DFC3', '#4A3430'),
            ('panda_rabbit', 'Panda Rabbit', '#F3F0EA', '#494652', '#302E38'),
        ):
            self.pets[skin] = {'type': 'rabbit', 'name': name, 'colors': {
                'body': QColor(body), 'patch': QColor(patch), 'outline': QColor(outline),
                'ear': QColor('#EAA5B3'), 'eye': QColor('#302B38'),
                'blush': QColor('#EAB0B9'),
            }}

        for skin, name, body, highlight, face, outline in (
            ('black_gorilla', 'Black Gorilla', '#383D49', '#616C7D', '#8E929C', '#20232D'),
            ('white_gorilla', 'White Gorilla', '#F1EDE4', '#FFFFFF', '#C3B3AA', '#55505B'),
        ):
            self.pets[skin] = {'type': 'gorilla', 'name': name, 'colors': {
                'body': QColor(body), 'highlight': QColor(highlight), 'face': QColor(face),
                'outline': QColor(outline), 'patch': QColor(highlight),
                'eye': QColor('#20222C'), 'blush': QColor('#DDA3A9'),
            }}

        self.pets['doge_dog'] = {'type': 'dog', 'name': 'Doge Dog', 'colors': {
            'body': QColor('#D9AA63'), 'shade': QColor('#B88445'),
            'patch': QColor('#FFF0CD'), 'outline': QColor('#48382D'),
            'eye': QColor('#302A26'), 'ear': QColor('#D99383'),
            'blush': QColor('#E2A083'),
        }}

        self.pets['shiba_inu_dog'] = {'type': 'dog', 'name': 'Shiba Inu Dog', 'colors': {
            'body': QColor('#DCA15A'), 'shade': QColor('#AD7139'),
            'patch': QColor('#FFF0D4'), 'outline': QColor('#493329'),
            'eye': QColor('#302A26'), 'ear': QColor('#D99383'),
            'blush': QColor('#E2A083'), 'vest': QColor('#F47724'),
            'vest_shadow': QColor('#BC491B'), 'vest_light': QColor('#FFB34D'),
        }}

        for skin, name, body, wing, belly, gold, outline in (
            ('emerald_dragon', 'Emerald Dragon', '#4F9B7C', '#78B9A1', '#F5D49A', '#E6B65F', '#283E38'),
            ('red_dragon', 'Red Dragon', '#CB443E', '#EA7550', '#F7CB68', '#F3B635', '#512D30'),
        ):
            self.pets[skin] = {'type': 'dragon', 'name': name, 'colors': {
                'body': QColor(body), 'wing': QColor(wing), 'belly': QColor(belly),
                'gold': QColor(gold), 'outline': QColor(outline), 'patch': QColor(belly),
                'eye': QColor('#F6D67B'), 'blush': QColor('#F1908C'),
            }}

        for skin, name, body, patch, gill, fin, outline in (
            ('pink_axolotl', 'Pink Axolotl', '#F7C7D8', '#FFE7ED', '#DB719E', '#EEA2C4', '#694658'),
            ('golden_axolotl', 'Golden Axolotl', '#F4CE79', '#FFF0BF', '#E59864', '#F4B979', '#71523D'),
        ):
            self.pets[skin] = {'type': 'axolotl', 'name': name, 'colors': {
                'body': QColor(body), 'patch': QColor(patch), 'gill': QColor(gill),
                'fin': QColor(fin), 'outline': QColor(outline),
                'eye': QColor('#352C40'), 'blush': QColor(gill),
            }}

        for skin, name, dark, outline, pad in (
            ('classic_panda', 'Classic Panda', '#343440', '#262633', '#656171'),
            ('brown_panda', 'Brown Panda', '#8C6953', '#4F3C36', '#B59177'),
        ):
            self.pets[skin] = {'type': 'panda', 'name': name, 'colors': {
                'body': QColor('#F7F1E6'), 'shade': QColor('#DED8CF'),
                'dark': QColor(dark), 'outline': QColor(outline), 'pad': QColor(pad),
                'patch': QColor(dark), 'eye': QColor(outline), 'blush': QColor('#E8A4AE'),
            }}

        for skin, name, head, body, wing, shade, outline in (
            ('normal_duck', 'Normal Duck', '#FFE798', '#FFE798', '#FFF2BF', '#DDBC66', '#675034'),
            ('azzamq_duck', 'AzzamQ Duck', '#32AD64', '#82452F', '#A35A38', '#633522', '#17182B'),
        ):
            self.pets[skin] = {'type': 'duck', 'name': name, 'colors': {
                'head': QColor(head), 'body': QColor(body), 'wing': QColor(wing),
                'shade': QColor(shade), 'outline': QColor(outline), 'patch': QColor(wing),
                'eye': QColor('#302A30'), 'blush': QColor('#EE9897'),
                'bill': QColor('#FFB52D'), 'bill_shadow': QColor('#B76420'),
            }}

        for skin, name, body, shade in (
            ('classic_penguin', 'Classic Penguin', '#354252', '#65778B'),
            ('blue_penguin', 'Blue Penguin', '#548AAF', '#85BCD4'),
        ):
            self.pets[skin] = {'type': 'penguin', 'name': name, 'colors': {
                'body': QColor(body), 'shade': QColor(shade), 'outline': QColor('#273342'),
                'patch': QColor('#FFF4DF'), 'belly_shadow': QColor('#DCDCCD'),
                'foot': QColor('#F4B04C'), 'eye': QColor('#29303C'), 'blush': QColor('#EFA3AF'),
            }}

    # ==================================================
    # BASIC STATE
    # ==================================================

    def set_state(self, state):
        self.state = state

    def set_skin(self, skin):
        if skin in self.pets:
            self.skin = skin
            self.state = "idle"
            self.tail_frame = 0
            self.ear_twitch = False
            self.curious_direction = 0

    def get_pet_type(self):
        return self.pets[self.skin]["type"]

    # ==================================================
    # ANIMATION CONTROL
    # ==================================================

    def next_tail_frame(self):
        self.tail_frame = (self.tail_frame + 1) % 4

    def next_idle_frame(self):
        self.idle_frame = 1 - self.idle_frame

    def set_ear_twitch(self, value):
        self.ear_twitch = value

    def set_curiosity(self, direction):
        self.curious_direction = direction

    # ==================================================
    # DRAW ROUTER
    # ==================================================

    def draw(self, painter: QPainter, x: int, y: int):
        draw_special(self, painter, x, y, self._draw_base)

    def _draw_base(self, painter: QPainter, x: int, y: int):
        if self.get_pet_type() == 'penguin':
            draw_penguin(self, painter, x, y)
            return
        if self.get_pet_type() == 'duck':
            draw_duck(self, painter, x, y)
            return
        if self.get_pet_type() == 'panda':
            draw_panda(self, painter, x, y)
            return
        if self.get_pet_type() == 'axolotl':
            draw_axolotl(self, painter, x, y)
            return
        if self.get_pet_type() == 'dragon':
            draw_dragon(self, painter, x, y)
            return
        if self.get_pet_type() == 'dog':
            draw_dog(self, painter, x, y)
            return
        if self.get_pet_type() == 'gorilla':
            draw_gorilla(self, painter, x, y)
            return
        if self.get_pet_type() == 'rabbit':
            draw_rabbit(self, painter, x, y)
            return
        if self.state in ('drowsy', 'sleeping'):
            self.draw_sleep_pose(painter, x, y)
            return
        if self.state in ('wall_look', 'climbing', 'slipping', 'landing', 'angry'):
            self.draw_wall_pose(painter, x, y)
            return
        if self.state == 'walking':
            self.draw_profile(painter, x, y)
            return
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, False)
        c = self.pets[self.skin]["colors"]
        phase = self.idle_frame
        state = self.state
        # Pose changes are anchored at the feet, keeping the pet on the desktop.
        painter.translate(x + 53, y + 84)
        if state == "stretch":
            painter.scale(.94, 1.08)
        elif state == "held":
            painter.rotate(-5 if phase else 5)
            painter.translate(0, -4)
        elif state == "settle":
            painter.scale(1.06, .9)
        elif state == "walking":
            painter.translate(0, -2 * phase)
            painter.rotate(-2 if phase else 2)
        elif state == "sniff":
            painter.translate(2 * phase, 0)
        elif state == "look":
            painter.rotate(-3 if phase else 3)
        elif state == "groom":
            painter.rotate(-3 * phase)
        elif self.get_pet_type() == "cat":
            painter.translate(self.curious_direction * 2 if state == "curious" else 0, -phase)
        painter.translate(-53, -84)
        self.draw_seated(painter, c)
        painter.restore()
        painter.save()
        painter.setFont(QFont("Segoe UI", 11))
        painter.setPen(QColor("#FFF0D6"))
        if state == "sleeping":
            painter.drawText(x + 83, y + 19 - phase * 3, "Zzz")
        elif state == "happy":
            painter.setPen(QColor("#F3A0A0"))
            painter.drawText(x + 86, y + 16 - phase * 2, "\u2665")
        elif state == "held":
            painter.drawText(x + 90, y + 13, "!")
        elif state in ("curious", "look"):
            painter.drawText(x + 88, y + 15, "?")
        painter.restore()

    def draw_seated(self, painter, c):
        """Faceted sitting pose shared by all skins and both desktop modes."""
        fox = self.get_pet_type() == 'fox'
        state = self.state
        breath = self.idle_frame if state == 'idle' else 0
        tail = (0, -3, 0, 3)[self.tail_frame]

        def shape(points, color, outline=True):
            painter.setPen(QPen(c['outline'], 3, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin) if outline else Qt.NoPen)
            painter.setBrush(color)
            painter.drawPolygon(QPolygon([QPoint(round(px),round(py)) for px,py in points]))

        def line(points, color, width=2):
            painter.setPen(QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPolyline(QPolygon([QPoint(round(px),round(py)) for px,py in points]))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0,0,0,35))
        painter.drawEllipse(24,79,69,6)
        # Tail has a distinct curved silhouette instead of a rectangular appendage.
        if fox:
            shape([(68,68),(81,61),(88,49+tail),(98,42+tail),(106,45+tail),
                   (107,55+tail),(101,70),(91,80),(76,81)],c['body'])
            shape([(91,49+tail),(98,44+tail),(104,46+tail),(105,54+tail),
                   (100,60+tail),(99,55+tail),(94,56+tail)],c['tail_tip'],False)
            line([(83,73),(91,67),(95,62)],c['stripe'],2)
        else:
            points=[(70,74),(87,76),(97,69+tail),(98,57+tail),(93,51+tail)]
            line(points,c['outline'],9)
            line(points,c['body'],5)
            line([(97,62+tail),(98,58+tail)],c['patch'],5)
        # Haunches support a tapered chest, with paws planted at the same baseline.
        shape([(31,71),(34,59-breath),(42,48-breath),(64,47-breath),
               (74,57-breath),(79,73),(74,80),(34,80)],c['body'])
        shape([(42,54-breath),(52,50-breath),(64,53-breath),(66,63),
               (60,74),(49,76),(41,68)],c['patch'],False)
        line([(37,65),(35,74),(40,76)],c['body'].darker(118),2)
        line([(72,65),(75,74),(69,76)],c['body'].darker(118),2)
        if state == 'held':
            shape([(40,70),(47,70),(46,88),(39,89),(36,86)],c['body'])
            shape([(60,70),(67,70),(71,86),(67,89),(60,87)],c['body'])
        else:
            shape([(38,72),(47,73),(49,79),(45,83),(33,83),(31,80),(33,76)],c['body'])
            shape([(62,73),(71,72),(76,77),(77,81),(74,83),(61,83),(58,79)],c['body'])
            line([(35,80),(44,80)],c['patch'],3)
            line([(63,80),(72,80)],c['patch'],3)
            line([(39,78),(39,81)],c['outline'],1)
            line([(67,78),(67,81)],c['outline'],1)

        painter.save()
        if state == 'curious':
            painter.translate(self.curious_direction*2,1)
            painter.translate(53,46)
            painter.rotate(self.curious_direction*4)
            painter.translate(-53,-46)
        if state == 'sniff':
            painter.translate(0,self.idle_frame)
        # Far ear, rounded cheeks and pointed ear tips match the walking artwork.
        ear_shift = -2 if self.ear_twitch else 0
        shape([(26,30),(23,15),(26,7 if fox else 12),(32,10 if fox else 14),
               (43,27)],c['body'])
        shape([(64,27),(74,9+ear_shift if fox else 14+ear_shift),
               (81,7+ear_shift if fox else 12+ear_shift),(84,17+ear_shift),(81,32)],c['body'])
        shape([(28,25),(27,14 if fox else 18),(36,25)],c['ear'],False)
        shape([(71,25),(79,14+ear_shift if fox else 18+ear_shift),(80,26)],c['ear'],False)
        if fox:
            head=[(27,25),(39,20),(64,20),(78,25),(85,36),(82,47),
                  (73,52),(63,58),(54,64),(44,60),(35,54),(24,48),(21,37)]
        else:
            head=[(27,27),(39,22),(66,22),(79,27),(85,37),(83,49),
                  (75,57),(63,61),(42,61),(30,56),(23,48),(21,37)]
        shape(head,c['body'])
        if fox:
            shape([(24,40),(36,42),(47,48),(54,55),(62,48),(75,42),
                   (83,40),(79,48),(69,53),(62,57),(54,61),(44,57),(34,51),(26,47)],c['patch'],False)
            shape([(42,23),(63,23),(61,28),(55,30),(51,35),(47,29)],c['stripe'],False)
        else:
            shape([(43,24),(51,23),(54,31),(50,35),(46,32)],c['patch'],False)
            shape([(56,23),(63,24),(63,30),(58,33)],c['patch'],False)
            shape([(39,48),(49,46),(54,48),(59,46),(69,49),(66,56),
                   (55,59),(44,56)],c['body'].lighter(108),False)
        # Expressive eyelids, cheeks, nose and mouth.
        look = self.curious_direction*2 if state == 'curious' else 0
        if state in ('blink','groom'):
            line([(34,40),(38,42),(43,40)],c['eye'],2)
            line([(64,40),(69,42),(73,40)],c['eye'],2)
        elif state in ('happy','stretch'):
            line([(33,41),(38,36),(43,41)],c['eye'],2)
            line([(64,41),(69,36),(74,41)],c['eye'],2)
        else:
            for ex in (36+look,66+look):
                painter.setPen(Qt.NoPen)
                painter.setBrush(c['eye'])
                painter.drawRoundedRect(ex,35,6,9 if state == 'held' else 8,2,2)
                painter.setBrush(QColor('#FFF7EA'))
                painter.drawRect(ex+1,36,2,2)
        line([(29,47),(35,48)],c['blush'],3)
        line([(73,48),(78,47)],c['blush'],3)
        shape([(50,48),(57,48),(54,52)],c['outline'],False)
        if state == 'held':
            painter.setPen(QPen(c['outline'],2))
            painter.setBrush(c['ear'])
            painter.drawEllipse(52,54,5,6)
        else:
            line([(54,52),(54,55),(50,56)],c['outline'],1)
            line([(54,55),(58,56)],c['outline'],1)
        if not fox:
            line([(25,48),(18,46)],c['outline'],1)
            line([(26,52),(18,53)],c['outline'],1)
            line([(81,48),(89,46)],c['outline'],1)
            line([(80,52),(88,53)],c['outline'],1)
        painter.restore()
        if state == 'groom':
            paw_y=46-self.idle_frame*4
            shape([(38,67),(33,paw_y+6),(35,paw_y),(42,paw_y-1),
                   (46,paw_y+5),(44,65)],c['body'])
            line([(36,paw_y+4),(43,paw_y+3)],c['patch'],3)

    def draw_profile(self, painter, x, y, pose=None):
        """Eight distance-driven poses, with separate walk and bounding run gaits."""
        c = self.pets[self.skin]['colors']
        fox = self.get_pet_type() == 'fox'
        running = self.running and pose is None
        phase = self.walk_phase % 8 if pose is None else 0
        angle = phase * math.pi / 4
        bob = (0, -1, -2, -1, 0, -1, -2, -1)[phase]
        if running:
            bob = (0, -2, -5, -3, 0, -1, -3, -1)[phase]
        painter.save()
        painter.translate(x, y)
        if self.facing < 0:
            painter.translate(114, 0)
            painter.scale(-1, 1)
        painter.setRenderHint(QPainter.Antialiasing, False)

        def block(px, py, w, h, color):
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawRect(int(px), int(py), int(w), int(h))

        def shape(points, color, outlined=True):
            painter.setPen(QPen(c['outline'], 3, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin) if outlined else Qt.NoPen)
            painter.setBrush(color)
            painter.drawPolygon(QPolygon([QPoint(int(px), int(py)) for px, py in points]))

        # Broad tapered fox tail, or a curling cat tail; root stays attached.
        tail_angle = self.walk_phase * math.pi / 4 if pose == 'angry' else angle
        sway = round(math.sin(tail_angle - .7) * (6 if pose == 'angry' else 3))
        if fox:
            shape([(38,58+bob),(28,54+bob),(21,43+sway),(10,38+sway),
                   (3,40+sway),(7,53+sway),(17,64+sway),(30,67+bob),(40,64+bob)], c['body'])
            shape([(4,41+sway),(11,40+sway),(18,44+sway),(15,49+sway),
                   (16,55+sway),(10,52+sway)], c['tail_tip'], False)
            block(24,59+bob,10,3,c['stripe'])
        else:
            painter.setPen(QPen(c['outline'], 8, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
            points = [QPoint(36,60+bob),QPoint(22,54+sway),QPoint(17,38+sway),QPoint(10,33+sway),QPoint(6,37+sway)]
            painter.drawPolyline(QPolygon(points))
            painter.setPen(QPen(c['body'], 4, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
            painter.drawPolyline(QPolygon(points))

        def leg(base, offset, far=False):
            a = angle + offset
            stride = round(math.sin(a) * (10 if running else 6))
            lift = round(max(0, math.cos(a)) * (7 if running else 5))
            foot = 84 - lift
            knee = base + round(stride * .4)
            shade = c['body'].darker(125) if far else c['body']
            shape([(base-3,62+bob),(base+4,62+bob),(knee+3,73+bob),
                   (base+stride+5,foot-4),(base+stride+5,foot),
                   (base+stride-3,foot),(knee-3,73+bob)], shade)
            block(base+stride-2,foot-3,6,3,c['patch'].darker(115) if far else c['patch'])

        # Far legs precede the torso, near legs overlap it.
        leg(43, math.pi, True)
        leg(73, .7 if running else 0, True)
        shape([(30,54+bob),(39,48+bob),(64,47+bob),(78,51+bob),
               (82,61+bob),(77,70+bob),(42,71+bob),(31,66+bob)], c['body'])
        shape([(56,61+bob),(77,58+bob),(77,67+bob),(66,69+bob),(53,68+bob)], c['patch'], False)
        if not fox:
            block(42,49+bob,5,8,c['patch'])
            block(52,49+bob,5,6,c['patch'])
        leg(39, 0)
        leg(76, .7 if running else math.pi)

        # Two ears and a stepped cheek silhouette keep the profile recognizable.
        hy = bob + (2 if running else 0)
        if pose == 'wall_look':
            hy -= 4
        elif pose == 'angry':
            hy += 2
        shape([(65,34+hy),(63,(20 if fox else 23)+hy),(69,(15 if fox else 19)+hy),(78,31+hy)], c['body'].darker(120))
        shape([(64,31+hy),(73,25+hy),(87,26+hy),(96,33+hy),
               (96,44+hy),(105 if fox else 101,47+hy),
               (105 if fox else 101,54+hy),(91,59+hy),(74,58+hy),
               (64,49+hy)], c['body'])
        shape([(74,30+hy),(75,(14 if fox else 20)+hy),(80,(10 if fox else 16)+hy),(87,29+hy)], c['body'])
        shape([(78,25+hy),(79,(16 if fox else 22)+hy),(83,26+hy)], c['ear'], False)
        shape([(80,46+hy),(91,43+hy),(95,47+hy),(103 if fox else 99,49+hy),
               (102 if fox else 98,53+hy),(89,56+hy),(80,53+hy)], c['patch'], False)
        block(102 if fox else 98,47+hy,5,4,c['outline'])
        block(89,35+hy,5,7,c['eye'])
        block(90,35+hy,2,2,QColor('#FFF7EA'))
        if pose == 'angry':
            block(87,33+hy,9,4,c['body'])
            painter.setPen(QPen(c['outline'], 2))
            painter.drawLine(86,33+hy,95,37+hy)
        block(83,45+hy,5,3,c['blush'])
        block(94,53+hy,5,2,c['outline'])
        if not fox:
            block(98,44+hy,7,1,c['outline'])
            block(99,56+hy,7,1,c['outline'])
        painter.restore()

    def draw_wall_pose(self, painter, x, y):
        c = self.pets[self.skin]['colors']
        fox = self.get_pet_type() == 'fox'
        state = self.state
        progress = getattr(self, 'wall_progress', 0)
        # Keep the familiar side silhouette for anticipation and recovery.
        if state in ('wall_look', 'landing', 'angry'):
            painter.save()
            if state == 'landing':
                squash = .22 * math.sin(math.pi * min(1, progress))
                painter.translate(x + 57, y + 84)
                painter.scale(1 + squash * .16, 1 - squash)
                painter.translate(-x - 57, -y - 84)
            self.draw_profile(painter, x, y, pose=state)
            painter.restore()
            if state == 'angry':
                painter.save()
                painter.setPen(QPen(QColor('#F07868'), 2))
                symbol_x = x + (58 if self.facing > 0 else 48)
                for ax, ay, bx, by in [(0,5,5,5),(5,5,5,0),(10,0,10,5),
                                      (10,5,15,5),(0,10,5,10),(5,10,5,15),
                                      (10,15,10,10),(10,10,15,10)]:
                    painter.drawLine(symbol_x+ax,y+8+ay,symbol_x+bx,y+8+by)
                painter.restore()
            return

        angle = self.walk_phase * math.pi / 4
        slip = state == 'slipping'
        reach = round(math.sin(angle) * 5)
        sway = round(math.sin(angle - .8) * 3)
        painter.save()
        painter.translate(x, y)
        if self.facing < 0:
            painter.translate(114, 0)
            painter.scale(-1, 1)
        painter.setRenderHint(QPainter.Antialiasing, False)
        # Loss of grip tips the whole body backward as it falls.
        if slip:
            painter.translate(75, 64)
            painter.rotate(-14 * min(1, progress))
            painter.translate(-75, -64)

        def shape(points, color, outline=True):
            painter.setPen(QPen(c['outline'], 3, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin) if outline else Qt.NoPen)
            painter.setBrush(color)
            painter.drawPolygon(QPolygon([QPoint(round(px),round(py)) for px,py in points]))

        def line(points, color, width):
            painter.setPen(QPen(c['outline'], width+3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            polygon = QPolygon([QPoint(round(px),round(py)) for px,py in points])
            painter.drawPolyline(polygon)
            painter.setPen(QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPolyline(polygon)

        # Tail hangs behind the haunches rather than sticking out like a box.
        if fox:
            shape([(62,60),(49,61),(38,65+sway),(24,60+sway),(21,66+sway),
                   (32,77+sway),(45,80+sway),(59,74),(67,69)],c['body'])
            shape([(24,63+sway),(31,67+sway),(35,66+sway),(38,74+sway),
                   (32,73+sway),(28,71+sway)],c['tail_tip'],False)
        else:
            line([(62,66),(46,75),(32,73+sway),(26,66+sway),(29,60+sway)],c['body'],4)
        # Far limbs sit behind a curved, leaning torso.
        line([(80,42),(94,43),(109,32-reach if not slip else 46)],c['body'].darker(125),5)
        line([(64,63),(80,54),(106,64+reach if not slip else 79)],c['body'].darker(125),6)
        shape([(51,60),(57,48),(66,39),(80,35),(88,43),(87,54),
               (77,68),(67,76),(56,75),(49,68)],c['body'])
        shape([(78,42),(86,44),(83,56),(72,69),(66,69),(73,56)],c['patch'],False)
        if not fox:
            line([(58,51),(65,55)],c['patch'],3)
            line([(53,58),(59,62)],c['patch'],3)
        # Bent near hind leg pushes against the wall; toes uncurl on slipping.
        line([(59,66),(76,57),(106 if not slip else 86,71-reach if not slip else 79)],c['body'],7)
        line([(106 if not slip else 84,71-reach if not slip else 79),
              (110 if not slip else 91,65-reach if not slip else 81)],c['patch'],5)
        # Same tapered muzzle and triangular ears as the walking profile.
        hy = -4 if not slip else 0
        shape([(69,28+hy),(69,17+hy),(74,13+hy),(81,27+hy)],c['body'].darker(120))
        shape([(66,29+hy),(75,22+hy),(89,23+hy),(97,30+hy),
               (97,38+hy),(106 if fox else 102,41+hy),(106 if fox else 102,48+hy),
               (93,53+hy),(76,51+hy),(66,43+hy)],c['body'])
        shape([(79,27+hy),(79,(8 if fox else 13)+hy),(84,(5 if fox else 10)+hy),
               (91,28+hy)],c['body'])
        shape([(82,22+hy),(83,(12 if fox else 17)+hy),(87,24+hy)],c['ear'],False)
        shape([(83,40+hy),(95,37+hy),(97,42+hy),(104 if fox else 100,43+hy),
               (103 if fox else 99,47+hy),(90,50+hy),(82,46+hy)],c['patch'],False)
        line([(103 if fox else 99,41+hy),(106 if fox else 102,41+hy)],c['outline'],3)
        painter.setPen(Qt.NoPen)
        painter.setBrush(c['eye'])
        painter.drawRect(89,29+hy,5,7 if not slip else 9)
        painter.setBrush(QColor('#FFF7EA'))
        painter.drawRect(90,29+hy,2,2)
        painter.setBrush(c['blush'])
        painter.drawRect(83,40+hy,5,3)
        # Alternating forepaw reaches, short elbow, and small visible claws.
        paw_y = 40+reach if not slip else 53
        paw_x = 111 if not slip else 98
        line([(81,48),(94,53),(paw_x,paw_y)],c['body'],6)
        line([(paw_x-3,paw_y),(paw_x,paw_y-5)],c['patch'],5)
        if not slip:
            painter.setPen(QPen(c['outline'],1))
            painter.drawLine(111,paw_y-5,114,paw_y-6)
            painter.drawLine(112,paw_y-2,114,paw_y-3)
        else:
            # Tiny motion marks emphasize the sudden release.
            painter.setPen(QPen(QColor('#B9CBD4'),2))
            painter.drawLine(111,26,111,33)
            painter.drawLine(117,31,117,39)
        painter.restore()

    def draw_sleep_pose(self, painter, x, y):
        """A curled silhouette, with an anchored tail and a gently breathing back."""
        c = self.pets[self.skin]['colors']
        fox = self.get_pet_type() == 'fox'
        asleep = self.state == 'sleeping'
        t = 1.0 if asleep else max(0, min(1, self.sleep_progress))
        settle = t * t * (3 - 2 * t)
        breath = round((1 - math.cos(self.breath_phase)) * .75) if asleep else 0
        head_drop = round(15 * settle)
        painter.save()
        painter.translate(x, y)
        painter.setRenderHint(QPainter.Antialiasing, False)

        def shape(points, color, border=True):
            painter.setPen(QPen(c['outline'], 3, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin) if border else Qt.NoPen)
            painter.setBrush(color)
            painter.drawPolygon(QPolygon([QPoint(round(px),round(py)) for px,py in points]))

        def line(points, color, width=2):
            painter.setPen(QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPolyline(QPolygon([QPoint(round(px),round(py)) for px,py in points]))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0,0,0,35))
        painter.drawEllipse(16,78,86,7)
        # Rounded, stepped back. Only the back rises, not the entire pet.
        shape([(27,70),(29,56-breath),(39,45-breath),(55,40-breath),
               (74,41-breath),(89,48-breath),(97,61),(96,72),
               (85,79),(42,80)], c['body'])
        if not fox:
            shape([(56,43-breath),(63,43-breath),(65,51-breath),(60,55-breath)],c['patch'],False)
            shape([(71,45-breath),(77,47-breath),(79,54-breath),(74,57-breath)],c['patch'],False)
        # Paws tucked underneath the resting cheek.
        shape([(22,73),(30,70),(45,72),(49,78),(45,81),(25,81),(20,78)],c['patch'])
        line([(29,76),(29,79)],c['outline'],1)
        line([(35,76),(35,79)],c['outline'],1)
        painter.save()
        painter.translate(0,head_drop)
        # The head nods down over three seconds rather than being flattened.
        shape([(21,42),(20,26 if fox else 30),(25,23 if fox else 27),(37,38)],c['body'].darker(110))
        shape([(19,40),(28,34),(44,34),(55,40),(59,51),(53,61),
               (40,65),(25,61),(17,52)],c['body'])
        shape([(39,37),(45,23 if fox else 27),(51,26 if fox else 30),(54,43)],c['body'])
        shape([(44,36),(47,29 if fox else 33),(50,38)],c['ear'],False)
        shape([(20,49),(29,51),(37,57),(46,51),(54,49),(52,58),
               (39,62),(26,58)],c['patch'],False)
        # Heavy lids close fully as the head settles.
        eye_y = 46
        if t < .45 and not asleep:
            line([(24,eye_y),(29,eye_y)],c['eye'],3)
            line([(43,eye_y),(48,eye_y)],c['eye'],3)
        else:
            line([(23,eye_y),(26,eye_y+2),(30,eye_y+1)],c['eye'],2)
            line([(42,eye_y+1),(46,eye_y+2),(49,eye_y)],c['eye'],2)
        shape([(34,53),(39,53),(37,56)],c['outline'],False)
        line([(37,56),(38,58)],c['outline'],1)
        line([(21,53),(25,54)],c['blush'],2)
        painter.restore()
        # Tail wraps around the front of the body while leaving the face visible.
        if fox:
            shape([(89,57),(99,62),(101,71),(96,80),(85,83),(60,83),
                   (49,79),(45,74),(54,70),(71,72),(84,69)],c['body'])
            shape([(47,74),(55,72),(65,74),(70,73),(69,78),(75,81),
                   (60,81),(51,78)],c['tail_tip'],False)
            line([(85,74),(78,77),(72,77)],c['stripe'],2)
        else:
            line([(90,61),(96,67),(94,75),(85,80),(66,80),(57,77)],c['outline'],9)
            line([(90,61),(96,67),(94,75),(85,80),(66,80),(57,77)],c['body'],5)
            line([(68,80),(73,80)],c['patch'],5)
        # Small rising pixel Zs instead of a large text label.
        if asleep:
            rise = round((self.breath_phase / (2 * math.pi) % 1) * 5)
            for zx, zy, size in [(72,28-rise,4),(83,19-rise,6)]:
                line([(zx,zy),(zx+size,zy),(zx,zy+size),(zx+size,zy+size)],QColor('#D8DDEA'),1)
        painter.restore()
