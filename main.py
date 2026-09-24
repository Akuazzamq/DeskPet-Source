import sys
import time
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QPoint, QRect, QSettings
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QCursor, QIcon, QPixmap, QRegion, QActionGroup, QPolygon
from PySide6.QtWidgets import QApplication, QWidget, QMenu, QMessageBox, QSystemTrayIcon, QInputDialog

from pet_engine import PetEngine
from app_icon import application_icon, get_type_icon, get_skin_icon
from behavior import Behavior, WALL_STATES
from idle_monitor import IdleMonitor
import startup
from time_tools import TimeTools
from fullscreen import FullscreenMonitor
from taskbar_motion import TaskbarMotion, floor_y


class DesktopPet(QWidget):
    def __init__(self, settings=None):
        super().__init__()
        self.setWindowIcon(application_icon())
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(130, 150)
        self.setMouseTracking(True)
        self.pet = PetEngine()
        self.behavior = Behavior(self.pet)
        self.idle = IdleMonitor()
        self.time_tools = TimeTools()
        self.settings = settings if settings is not None else QSettings('DesktoPet', 'DesktoPet')  # Keep existing user preferences after rebranding.
        self.time_bar_style = self.settings.value('time_bar_style', 'pixel')
        if self.time_bar_style not in ('pixel', 'comic', 'wood', 'cloud', 'arcade'):
            self.time_bar_style = 'pixel'
        self.pet.set_skin(self.settings.value('pet', 'cream_cat'))
        self.behavior.wander = self.settings.value('wander', True, type=bool)
        self.behavior.sleep_enabled = self.settings.value('sleep', True, type=bool)
        self.mode = self.settings.value('mode', 'desktop')
        if self.mode not in ('desktop', 'taskbar'):
            self.mode = 'desktop'
        self.behavior.taskbar = self.mode == 'taskbar'
        self.monitor_name = self.settings.value('monitor', '')
        self.fullscreen = FullscreenMonitor()
        self.hide_fullscreen = self.settings.value('hide_fullscreen', True, type=bool)
        self.hidden_for_fullscreen = False
        self.fullscreen_check = 0
        self.motion = TaskbarMotion()
        self.last_tick = time.monotonic()
        self.returning = False
        self.hovered = False
        self.dragging = False
        self.pressed = False
        self.drag_offset = QPoint()
        self.press_position = QPoint()
        self.stroke_x = None
        self.stroke_direction = 0
        self.stroke_turns = 0
        self.stroke_time = 0
        self.menu_open = False
        self.current_time = ''
        self.move_to_bottom_right()
        saved = self.settings.value('position')
        if isinstance(saved, QPoint):
            self.move(saved)
            self.clamp_position()
        if self.mode == 'taskbar':
            self.move(self.x(), floor_y(self.taskbar_screen().availableGeometry()))
            self.constrain_taskbar()
        self.setup_tray()
        QApplication.instance().screenRemoved.connect(self.screen_changed)
        QApplication.instance().screenAdded.connect(self.screen_changed)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_behavior)
        self.timer.start(50)
        QApplication.instance().aboutToQuit.connect(self.save_settings)

    def save_settings(self):
        self.settings.setValue('hide_fullscreen', self.hide_fullscreen)
        self.settings.setValue('mode', self.mode)
        self.settings.setValue('monitor', self.monitor_name)
        self.settings.setValue('pet', self.pet.skin)
        self.settings.setValue('position', self.pos())
        self.settings.setValue('wander', self.behavior.wander)
        self.settings.setValue('sleep', self.behavior.sleep_enabled)
        self.settings.setValue('time_bar_style', self.time_bar_style)
        self.settings.sync()

    def move_to_bottom_right(self):
        area = QApplication.primaryScreen().availableGeometry()
        self.move(area.right() - self.width() - 10, area.bottom() - self.height() - 10)

    def clamp_position(self):
        screen = QApplication.screenAt(self.frameGeometry().center()) or QApplication.primaryScreen()
        area = screen.availableGeometry()
        self.move(max(area.left(), min(self.x(), area.right() - self.width() + 1)),
                  max(area.top(), min(self.y(), area.bottom() - self.height() + 1)))

    def taskbar_screen(self):
        return next((s for s in QApplication.screens() if s.name() == self.monitor_name),
                    QApplication.primaryScreen())

    def screen_changed(self, *args):
        if self.pet.state in WALL_STATES:
            self.behavior.enter('idle')
        self.motion.reset()
        if self.mode == 'taskbar':
            self.constrain_taskbar()
        else:
            self.clamp_position()

    def constrain_taskbar(self):
        area = self.taskbar_screen().availableGeometry()
        self.move(max(area.left(), min(self.x(), area.right() - self.width() + 1)),
                  floor_y(area) - self.pet.wall_height)

    def set_mode(self, mode):
        if mode == self.mode:
            return
        self.mode = mode
        self.behavior.taskbar = mode == 'taskbar'
        self.behavior.next_walk = time.monotonic() + 1.5
        self.motion.reset()
        self.behavior.enter('idle')
        self.returning = mode == 'taskbar'
        if mode == 'desktop':
            self.clamp_position()
        self.save_settings()
        self.update()

    def select_monitor(self, name):
        self.monitor_name = name
        if self.pet.state in WALL_STATES:
            self.behavior.enter('idle')
        self.motion.reset()
        if self.mode == 'taskbar':
            self.constrain_taskbar()
        self.save_settings()

    def setup_tray(self):
        self.tray = None
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(application_icon(), self)
        self.tray.setToolTip('DeskPet')
        menu = QMenu(self)
        menu.aboutToShow.connect(lambda: self.populate_menu(menu, tray=True))
        menu.aboutToHide.connect(self.save_settings)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.show_pet() if reason == QSystemTrayIcon.DoubleClick else None)
        self.tray.show()

    def show_pet(self):
        self.hidden_for_fullscreen = False
        self.fullscreen_check = time.monotonic() + 5
        self.show()
        self.screen_changed()
        self.raise_()

    def update_behavior(self):
        now = time.monotonic()
        dt = min(.1, max(0, now - self.last_tick))
        self.last_tick = now
        self.current_time = datetime.now().strftime('%H:%M:%S')
        if self.time_tools.tick():
            self.time_tools.mode = 'timer'
            if self.tray:
                self.tray.showMessage('DeskPet Timer', 'Time is up!', QSystemTrayIcon.Information, 5000)
        if now >= self.fullscreen_check and not self.pressed and not self.menu_open:
            self.fullscreen_check = now + .75
            covered = self.hide_fullscreen and self.fullscreen.covers(int(self.winId()))
            if covered and self.isVisible():
                self.hide()
                self.hidden_for_fullscreen = True
            elif not covered and self.hidden_for_fullscreen:
                self.show()
                self.hidden_for_fullscreen = False
        if self.hidden_for_fullscreen:
            return
        if not self.menu_open and not self.pressed:
            if self.returning and self.mode == 'taskbar':
                area = self.taskbar_screen().availableGeometry()
                target = floor_y(area)
                distance = target - self.y()
                step = min(abs(distance), max(1, round(360 * dt)))
                self.move(max(area.left(), min(self.x(), area.right() - self.width() + 1)),
                          self.y() + (step if distance > 0 else -step))
                if abs(target - self.y()) < 1:
                    self.returning = False
                    self.behavior.now = now
                    self.behavior.interact('settle', .65)
            else:
                delta = QCursor.pos() - self.frameGeometry().center()
                previous = self.pet.state
                self.behavior.tick(now, self.idle.seconds(),
                                   delta.x() ** 2 + delta.y() ** 2 < 160 ** 2,
                                   -1 if delta.x() < -20 else 1 if delta.x() > 20 else 0)
                if self.mode == 'taskbar':
                    self.constrain_taskbar()
                    if self.pet.state == 'walking' and not self.behavior.paused:
                        if not self.behavior.wander:
                            self.behavior.enter('idle')
                        else:
                            area = self.taskbar_screen().availableGeometry()
                            if self.motion.target is None and now >= self.behavior.next_climb and self.motion.rng.random() < .3:
                                self.motion.x = float(self.x())
                                self.motion.target = self.motion.rng.choice((area.left(), area.right() - self.width() + 1))
                                self.motion.running = True
                            x, direction, arrived = self.motion.step(self.x(), area.left(),
                                area.right() - self.width() + 1, dt, self.pet.get_pet_type() == 'fox')
                            self.behavior.until = now + 1  # Destination owns the end of the trip.
                            self.move(x, floor_y(area))
                            self.pet.facing = direction
                            self.pet.walk_phase = int(self.motion.phase)
                            self.pet.running = self.motion.running
                            if arrived:
                                self.behavior.enter('idle')
                                rest = self.behavior.rng.uniform(1.2, 3.0)
                                self.behavior.next_walk = now + rest
                                self.behavior.next_action = now + rest + 2
                                at_left = x <= area.left() + 1
                                at_right = x >= area.right() - self.width()
                                if at_left or at_right:
                                    self.behavior.start_wall(-1 if at_left else 1)
                    if self.pet.state != 'walking':
                        self.motion.reset()
        # No invisible window area intercepts taskbar buttons below the feet.
        if self.mode == 'taskbar':
            self.setMask(QRegion(0, 0 if self.show_time() else 45, 130, 134 if self.show_time() else 89))
        else:
            self.clearMask()
        self.update()

    def happy(self):
        if self.behavior.paused:
            return
        self.idle.activity()
        self.behavior.now = time.monotonic()
        if self.pet.state in ('sleeping', 'drowsy'):
            self.behavior.interact('stretch', 1.5)
        else:
            self.behavior.interact()
        self.update()

    def show_time(self):
        return self.mode == 'desktop' or self.hovered or self.time_tools.mode != 'clock'

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.show_time():
            self.draw_clock(painter)
        self.pet.draw(painter, 8, 48)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressed = True
            self.dragging = False
            self.press_position = event.globalPosition().toPoint()
            self.drag_offset = self.press_position - self.pos()
            self.idle.activity()
            event.accept()

    def mouseMoveEvent(self, event):
        self.idle.activity()
        if self.pressed and event.buttons() & Qt.LeftButton:
            if (event.globalPosition().toPoint() - self.press_position).manhattanLength() >= QApplication.startDragDistance():
                self.dragging = True
                if not self.behavior.paused:
                    self.behavior.interact('held', 0)
            if self.dragging:
                self.move(event.globalPosition().toPoint() - self.drag_offset)
            event.accept()
            return
        now = time.monotonic()
        point = event.position().toPoint()
        if not QRect(28, 55, 70, 55).contains(point) or self.behavior.paused:
            self.reset_strokes()
            return
        if now - self.stroke_time > 1:
            self.reset_strokes()
        if self.stroke_x is not None:
            dx = point.x() - self.stroke_x
            if abs(dx) < 5:
                return
            direction = 1 if dx > 0 else -1
            if self.stroke_direction and direction != self.stroke_direction:
                self.stroke_turns += 1
            self.stroke_direction = direction
            if self.stroke_turns >= 3:
                self.happy()
                self.stroke_turns = 0
        self.stroke_x = point.x()
        self.stroke_time = now

    def reset_strokes(self):
        self.stroke_x = None
        self.stroke_direction = 0
        self.stroke_turns = 0

    def enterEvent(self, event):
        self.hovered = True

    def leaveEvent(self, event):
        self.hovered = False
        self.reset_strokes()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.pressed:
            if self.dragging:
                if self.mode == 'taskbar':
                    screen = QApplication.screenAt(self.frameGeometry().center()) or QApplication.primaryScreen()
                    self.monitor_name = screen.name()
                    self.returning = True
                    self.motion.reset()
                else:
                    self.clamp_position()
                if not self.behavior.paused:
                    self.behavior.interact('settle', .65)
                self.save_settings()
            else:
                self.happy()
            self.pressed = self.dragging = False
            event.accept()

    def change_pet(self, pet_id):
        self.pet.set_skin(pet_id)
        self.settings.setValue('skin/' + self.pet.get_pet_type(), self.pet.skin)
        self.motion.reset()
        self.behavior.enter('idle')
        self.behavior.tail_left = 0
        self.reset_strokes()
        self.save_settings()
        self.update()

    def toggle_pause(self, checked):
        self.behavior.paused = checked
        self.behavior.enter('idle')

    def toggle_startup(self, checked):
        try:
            startup.set_enabled(checked)
        except OSError as error:
            QMessageBox.warning(self, "Startup setting", str(error))

    def change_type(self, kind):
        if kind == self.pet.get_pet_type():
            return
        candidates = [key for key, data in self.pet.pets.items() if data['type'] == kind]
        if not candidates:
            return
        self.settings.setValue('skin/' + self.pet.get_pet_type(), self.pet.skin)
        remembered = self.settings.value('skin/' + kind, candidates[0])
        self.change_pet(remembered if remembered in candidates else candidates[0])

    def select_time_mode(self, mode):
        self.time_tools.mode = mode
        self.update()

    def select_time_bar_style(self, style):
        if style not in ('pixel', 'comic', 'wood', 'cloud', 'arcade'):
            return
        self.time_bar_style = style
        self.save_settings()
        self.update()

    def custom_timer(self):
        minutes, ok = QInputDialog.getInt(self, 'Timer', 'Duration (minutes):', 25, 1, 1440)
        if ok:
            self.time_tools.start_timer(minutes * 60)

    def populate_menu(self, menu, tray=False):
        menu.clear()
        for group in menu.findChildren(QActionGroup):
            group.deleteLater()
        if tray:
            menu.addAction('Show pet', self.show_pet)
            menu.addSeparator()

        def radio(parent, options, selected, callback, icon_getter=None):
            group = QActionGroup(parent)
            group.setExclusive(True)
            for label, value in options:
                action = parent.addAction(label)
                if icon_getter:
                    action.setIcon(icon_getter(value, 20))
                action.setCheckable(True)
                action.setChecked(value == selected)
                group.addAction(action)
                action.triggered.connect(lambda checked=False, v=value: callback(v))

        pets = menu.addMenu('Pet')
        radio(pets.addMenu('Type'), [('Cat', 'cat'), ('Fox', 'fox'), ('Rabbit', 'rabbit'), ('Gorilla', 'gorilla'), ('Dog', 'dog'), ('Dragon', 'dragon'), ('Axolotl', 'axolotl'), ('Panda', 'panda'), ('Duck', 'duck'), ('Penguin', 'penguin')],
              self.pet.get_pet_type(), self.change_type, icon_getter=get_type_icon)
        skin_options = [(data['name'].removesuffix(' Cat').removesuffix(' Fox').removesuffix(' Rabbit').removesuffix(' Gorilla').removesuffix(' Dog').removesuffix(' Dragon').removesuffix(' Axolotl').removesuffix(' Panda').removesuffix(' Duck').removesuffix(' Penguin'), key)
                        for key, data in self.pet.pets.items() if data['type'] == self.pet.get_pet_type()]
        radio(pets.addMenu('Skin'), skin_options, self.pet.skin, self.change_pet, icon_getter=get_skin_icon)
        pets.addSeparator()
        pets.addAction('Pet / Wake up', self.happy)

        modes = menu.addMenu('Position mode')
        radio(modes, [('Desktop (stay in place)', 'desktop'), ('Taskbar', 'taskbar')],
              self.mode, self.set_mode)
        monitors = modes.addMenu('Taskbar monitor')
        monitors.setEnabled(self.mode == 'taskbar')
        radio(monitors, [(screen.name(), screen.name()) for screen in QApplication.screens()],
              self.taskbar_screen().name(), self.select_monitor)
        modes.addAction('Move to Bottom Right', self.move_to_bottom_right)

        clocks = menu.addMenu('Time')
        radio(clocks, [('Clock', 'clock'), ('Timer', 'timer'), ('Stopwatch', 'stopwatch')],
              self.time_tools.mode, self.select_time_mode)
        styles = clocks.addMenu('Time bar style')
        radio(styles, [('Classic pixel', 'pixel'), ('Comic pop', 'comic'),
                       ('Cozy wood', 'wood'), ('Cloud dream', 'cloud'),
                       ('Arcade machine', 'arcade')],
              self.time_bar_style, self.select_time_bar_style)
        clocks.addSeparator()
        timer = clocks.addMenu('Timer controls')
        for minutes in (5, 15, 25, 45, 60):
            timer.addAction(f'Start {minutes} minutes', lambda checked=False, m=minutes: self.time_tools.start_timer(m * 60))
        timer.addAction('Custom duration...', self.custom_timer)
        timer.addSeparator()
        action = timer.addAction('Pause' if self.time_tools.deadline is not None else 'Start / Resume', self.time_tools.toggle_timer)
        action.setEnabled(not self.time_tools.finished)
        timer.addAction('Reset', self.time_tools.reset_timer)
        stopwatch = clocks.addMenu('Stopwatch controls')
        stopwatch.addAction('Pause' if self.time_tools.started is not None else 'Start / Resume', self.time_tools.toggle_stopwatch)
        stopwatch.addAction('Reset', self.time_tools.reset_stopwatch)

        animations = menu.addMenu('Behavior')
        wander = animations.addAction('Walk / run in Taskbar Mode')
        wander.setCheckable(True)
        wander.setChecked(self.behavior.wander)
        wander.setEnabled(self.mode == 'taskbar')
        wander.toggled.connect(lambda checked: setattr(self.behavior, 'wander', checked))
        sleep = animations.addAction('Sleep after 3 minutes AFK')
        sleep.setCheckable(True)
        sleep.setChecked(self.behavior.sleep_enabled)
        sleep.toggled.connect(lambda checked: setattr(self.behavior, 'sleep_enabled', checked))
        pause = animations.addAction('Pause pet animations')
        pause.setCheckable(True)
        pause.setChecked(self.behavior.paused)
        pause.toggled.connect(self.toggle_pause)

        settings = menu.addMenu('Settings')
        fullscreen = settings.addAction('Hide during fullscreen')
        fullscreen.setCheckable(True)
        fullscreen.setChecked(self.hide_fullscreen)
        fullscreen.toggled.connect(lambda checked: setattr(self, 'hide_fullscreen', checked))
        if sys.platform == 'win32':
            login = settings.addAction('Start with Windows')
            login.setCheckable(True)
            login.setChecked(startup.enabled())
            login.toggled.connect(self.toggle_startup)
        menu.addSeparator()
        menu.addAction('Open dashboard', self.open_dashboard)
        menu.addAction('Quit DeskPet', QApplication.quit)

    def open_dashboard(self):
        if not hasattr(self, 'dashboard'):
            from dashboard import Dashboard
            self.dashboard = Dashboard(self)
        self.dashboard.setWindowState((self.dashboard.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()
        self.show_pet()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        self.populate_menu(menu)
        self.menu_open = True
        try:
            menu.exec(event.globalPos())
        finally:
            self.menu_open = False
            self.save_settings()
            menu.deleteLater()

    def draw_clock(self, painter):
        if self.time_bar_style == 'comic':
            self.draw_comic_clock(painter)
            return
        if self.time_bar_style == 'wood':
            self.draw_wood_clock(painter)
            return
        if self.time_bar_style == 'cloud':
            self.draw_cloud_clock(painter)
            return
        if self.time_bar_style == 'arcade':
            self.draw_arcade_clock(painter)
            return
        painter.setRenderHint(
            QPainter.Antialiasing,
            False
        )

        bubble = QRect(
            18,
            5,
            88,
            32
        )

        painter.setPen(
            QPen(
                QColor("#55566D"),
                3
            )
        )

        painter.setBrush(
            QColor("#242631")
        )

        painter.drawRect(
            bubble
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor("#55566D")
        )

        painter.drawRect(
            56,
            37,
            10,
            4
        )

        painter.setBrush(
            QColor("#242631")
        )

        painter.drawRect(
            59,
            37,
            4,
            5
        )

        painter.setPen(
            QColor("#FFFFFF")
        )

        font = QFont(
            "Consolas",
            11
        )

        font.setBold(
            True
        )

        painter.setFont(
            font
        )

        if self.time_tools.mode == 'clock':
            painter.drawText(bubble, Qt.AlignCenter, self.current_time)
        else:
            label, value = self.time_tools.display()
            painter.setFont(QFont('Segoe UI', 6))
            painter.setPen(QColor('#F3BE76') if self.time_tools.finished and self.time_tools.mode == 'timer' else QColor('#B7C5DD'))
            painter.drawText(QRect(19, 6, 86, 11), Qt.AlignCenter, label)
            painter.setFont(QFont('Consolas', 10, QFont.Bold))
            painter.setPen(QColor("#6E4747"))
            painter.drawText(QRect(19, 17, 86, 19), Qt.AlignCenter, value)
        self.draw_species_time_trim(painter, 'pixel')

    def draw_comic_clock(self, painter):
        """Bright comic speech bubble shared by clock, timer and stopwatch."""
        painter.setRenderHint(QPainter.Antialiasing, False)
        bubble = QRect(14, 4, 98, 34)

        # Cyan and magenta misregistration gives the bubble a printed-comic pop.
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor('#21D4FD'))
        painter.drawRect(bubble.translated(-3, 3))
        painter.setBrush(QColor('#FF3CAC'))
        painter.drawRect(bubble.translated(4, -2))

        painter.setPen(QPen(QColor('#17121F'), 3))
        painter.setBrush(QColor('#FFF4C7'))
        painter.drawRect(bubble)
        tail = QPolygon([QPoint(51, 37), QPoint(66, 37), QPoint(58, 45), QPoint(57, 38)])
        painter.drawPolygon(tail)

        # Halftone corner dots remain subtle enough to keep the digits readable.
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor('#F6C945'))
        for x, y in ((19, 9), (25, 9), (19, 15), (106, 27), (100, 27), (106, 21)):
            painter.drawRect(x, y, 2, 2)

        painter.setPen(QColor('#17121F'))
        if self.time_tools.mode == 'clock':
            painter.setFont(QFont('Consolas', 12, QFont.Black))
            painter.drawText(bubble, Qt.AlignCenter, self.current_time)
        else:
            label, value = self.time_tools.display()
            painter.setFont(QFont('Segoe UI', 6, QFont.Bold))
            painter.drawText(QRect(15, 6, 96, 11), Qt.AlignCenter, label.upper())
            painter.setFont(QFont('Consolas', 10, QFont.Black))
            painter.setPen(QColor('#D51E54') if self.time_tools.finished and self.time_tools.mode == 'timer' else QColor('#17121F'))
            painter.drawText(QRect(15, 17, 96, 19), Qt.AlignCenter, value)
        self.draw_species_time_trim(painter, 'comic')

    def draw_time_text(self, painter, bubble, main_color, accent_color):
        """Render consistent time content inside a themed pixel bar."""
        if self.time_tools.mode == 'clock':
            painter.setFont(QFont('Consolas', 11, QFont.Bold))
            painter.setPen(main_color)
            painter.drawText(bubble, Qt.AlignCenter, self.current_time)
            return
        label, value = self.time_tools.display()
        painter.setFont(QFont('Segoe UI', 6, QFont.Bold))
        painter.setPen(accent_color)
        painter.drawText(QRect(bubble.x(), bubble.y() + 1, bubble.width(), 11), Qt.AlignCenter, label.upper())
        painter.setFont(QFont('Consolas', 10, QFont.Bold))
        painter.setPen(QColor('#D94A45') if self.time_tools.finished and self.time_tools.mode == 'timer' else main_color)
        painter.drawText(QRect(bubble.x(), bubble.y() + 12, bubble.width(), 18), Qt.AlignCenter, value)

    def draw_wood_clock(self, painter):
        painter.setRenderHint(QPainter.Antialiasing, False)
        bubble = QRect(16, 6, 94, 32)

        # Blocky posts and rope make the panel look like a tiny hanging sign.
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor('#6B4028'))
        painter.drawRect(24, 2, 4, 7)
        painter.drawRect(98, 2, 4, 7)
        painter.setBrush(QColor('#D4A15E'))
        painter.drawRect(25, 2, 2, 6)
        painter.drawRect(99, 2, 2, 6)

        painter.setPen(QPen(QColor('#3B251C'), 3))
        painter.setBrush(QColor('#8F5734'))
        painter.drawRect(bubble)
        painter.setPen(QPen(QColor('#C88749'), 2))
        painter.drawLine(20, 11, 105, 11)
        painter.drawLine(20, 33, 105, 33)
        painter.setPen(QPen(QColor('#6B4028'), 1))
        painter.drawLine(36, 14, 48, 14)
        painter.drawLine(83, 30, 102, 30)
        painter.drawLine(23, 27, 31, 27)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor('#E8C176'))
        for x in (21, 104):
            painter.drawRect(x, 17, 3, 3)
            painter.drawRect(x, 28, 3, 3)
        self.draw_time_text(painter, bubble, QColor('#FFF1C4'), QColor('#FFD37D'))
        self.draw_species_time_trim(painter, 'wood')

    def draw_cloud_clock(self, painter):
        painter.setRenderHint(QPainter.Antialiasing, False)
        bubble = QRect(18, 6, 90, 32)

        # Pixel steps create a cloud silhouette without antialiased curves.
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor('#6D67B5'))
        painter.drawRect(15, 14, 98, 20)
        painter.drawRect(22, 8, 26, 30)
        painter.drawRect(46, 3, 34, 35)
        painter.drawRect(78, 9, 28, 29)
        painter.drawRect(54, 38, 9, 5)

        painter.setBrush(QColor('#EAF4FF'))
        painter.drawRect(17, 13, 94, 19)
        painter.drawRect(24, 7, 23, 29)
        painter.drawRect(48, 5, 31, 31)
        painter.drawRect(80, 10, 24, 26)
        painter.drawRect(55, 35, 7, 5)
        painter.setBrush(QColor('#BBD7F5'))
        painter.drawRect(21, 31, 84, 4)
        painter.drawRect(57, 39, 3, 4)

        # Tiny stars give the quiet night-sky theme a readable pixel signature.
        painter.setBrush(QColor('#FFD866'))
        painter.drawRect(13, 5, 2, 6); painter.drawRect(11, 7, 6, 2)
        painter.drawRect(112, 8, 2, 5); painter.drawRect(110, 10, 6, 2)
        self.draw_time_text(painter, bubble, QColor('#27345D'), QColor('#7869B3'))
        self.draw_species_time_trim(painter, 'cloud')

    PIXEL_DIGITS = {
        '0': ('111', '101', '101', '101', '111'),
        '1': ('010', '110', '010', '010', '111'),
        '2': ('111', '001', '111', '100', '111'),
        '3': ('111', '001', '111', '001', '111'),
        '4': ('101', '101', '111', '001', '001'),
        '5': ('111', '100', '111', '001', '111'),
        '6': ('111', '100', '111', '101', '111'),
        '7': ('111', '001', '010', '010', '010'),
        '8': ('111', '101', '111', '101', '111'),
        '9': ('111', '101', '111', '001', '111'),
        ':': ('0', '1', '0', '1', '0'),
    }

    def draw_pixel_digits(self, painter, text, area, color, scale=2):
        widths = [len(self.PIXEL_DIGITS.get(char, ('000',))[0]) for char in text]
        total = sum(widths) * scale + max(0, len(text) - 1) * scale
        x = area.x() + (area.width() - total) // 2
        y = area.y() + (area.height() - 5 * scale) // 2
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        for char, width in zip(text, widths):
            glyph = self.PIXEL_DIGITS.get(char)
            if glyph:
                for row, pixels in enumerate(glyph):
                    for col, pixel in enumerate(pixels):
                        if pixel == '1':
                            painter.drawRect(x + col * scale, y + row * scale, scale, scale)
            x += (width + 1) * scale

    def draw_arcade_clock(self, painter):
        painter.setRenderHint(QPainter.Antialiasing, False)
        cabinet = QRect(12, 2, 106, 41)

        # Compact arcade cabinet: marquee, dark CRT, control deck and joystick.
        painter.setPen(QPen(QColor('#1A132B'), 3))
        painter.setBrush(QColor('#7246B3'))
        painter.drawRect(cabinet)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor('#F13C77'))
        painter.drawRect(16, 5, 98, 7)
        painter.setBrush(QColor('#FFCE45'))
        painter.drawRect(21, 7, 8, 2)
        painter.drawRect(101, 7, 8, 2)

        screen = QRect(20, 14, 90, 20)
        painter.setPen(QPen(QColor('#251B38'), 2))
        painter.setBrush(QColor('#101A26'))
        painter.drawRect(screen)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor('#203747'))
        for y in range(17, 33, 4):
            painter.drawRect(22, y, 86, 1)

        painter.setBrush(QColor('#32214C'))
        painter.drawRect(17, 36, 96, 5)
        painter.setBrush(QColor('#37E6A5'))
        painter.drawRect(26, 37, 3, 3)
        painter.setBrush(QColor('#FFCE45'))
        painter.drawRect(101, 37, 3, 3)
        painter.setBrush(QColor('#F13C77'))
        painter.drawRect(106, 37, 3, 3)
        painter.setBrush(QColor('#1A132B'))
        painter.drawRect(31, 40, 4, 5)
        painter.drawRect(96, 40, 4, 5)

        value = self.current_time if self.time_tools.mode == 'clock' else self.time_tools.display()[1]
        color = QColor('#FF5370') if self.time_tools.finished and self.time_tools.mode == 'timer' else QColor('#54F7C5')
        scale = 3 if len(value) <= 5 else 2
        self.draw_pixel_digits(painter, value, screen.adjusted(2, 1, -2, -1), color, scale)
        self.draw_species_time_trim(painter, 'arcade')

    def draw_species_time_trim(self, painter, style):
        """Add a small pixel habitat signature without obscuring the time."""
        kind = self.pet.get_pet_type()
        colors = {
            'cat': QColor('#F3A0A0'), 'fox': QColor('#F28A3D'),
            'rabbit': QColor('#F0AFC1'), 'gorilla': QColor('#8B94A6'),
            'dog': QColor('#E8B85D'), 'dragon': QColor('#F05A42'),
            'axolotl': QColor('#E983B2'), 'panda': QColor('#66B85A'),
            'duck': QColor('#55C8D8'), 'penguin': QColor('#8EDBFF'),
        }
        accent = colors.get(kind, QColor('#FFFFFF'))
        trim_y = {'pixel': 35, 'comic': 35, 'wood': 34, 'cloud': 32, 'arcade': 9}.get(style, 35)
        trim_x = {'pixel': (22, 102), 'comic': (18, 108), 'wood': (20, 106),
                  'cloud': (22, 104), 'arcade': (31, 99)}.get(style, (22, 102))
        painter.setPen(Qt.NoPen)
        painter.setBrush(accent)
        painter.drawRect(trim_x[0], trim_y, trim_x[1] - trim_x[0], 2)

        if kind == 'penguin':
            # A restrained ice edge and two snow pixels.
            painter.setBrush(QColor('#DDF6FF'))
            painter.drawRect(16, 3, 9, 2); painter.drawRect(105, 3, 9, 2)
            painter.drawRect(18, 5, 2, 3); painter.drawRect(109, 5, 2, 3)
            painter.setBrush(accent)
            painter.drawRect(13, 12, 2, 2); painter.drawRect(115, 17, 2, 2)
        elif kind == 'panda':
            # Short bamboo corner brackets stay inside the bar footprint.
            painter.setBrush(QColor('#438B45'))
            painter.drawRect(14, 7, 2, 13); painter.drawRect(114, 20, 2, 13)
            painter.setBrush(QColor('#72C45A'))
            painter.drawRect(16, 8, 5, 2); painter.drawRect(11, 15, 4, 2)
            painter.drawRect(109, 22, 5, 2); painter.drawRect(116, 28, 4, 2)
        elif kind == 'dragon':
            # Small corner flames, clear of the time display.
            painter.setBrush(QColor('#FFB52E'))
            painter.drawRect(14, 29, 5, 7); painter.drawRect(111, 29, 5, 7)
            painter.drawRect(16, 26, 2, 4); painter.drawRect(112, 25, 2, 5)
            painter.setBrush(QColor('#F04B32'))
            painter.drawRect(16, 32, 2, 4); painter.drawRect(112, 32, 2, 4)
        elif kind == 'axolotl':
            # Small bubbles and ripples remain close to the frame.
            painter.setBrush(QColor('#91E5EE'))
            for x, y, size in ((14, 8, 3), (18, 16, 2), (114, 8, 2), (110, 15, 3)):
                painter.drawRect(x, y, size, size)
            painter.drawRect(14, 40, 10, 2); painter.drawRect(106, 40, 10, 2)
        elif kind == 'duck':
            # Two short pond ripples and one tiny reed.
            painter.setBrush(QColor('#62D6E8'))
            painter.drawRect(14, 39, 12, 2); painter.drawRect(104, 39, 12, 2)
            painter.drawRect(17, 42, 7, 1); painter.drawRect(106, 42, 7, 1)
            painter.setBrush(QColor('#78A94B'))
            painter.drawRect(14, 31, 2, 8); painter.drawRect(17, 34, 2, 5)
        elif kind == 'rabbit':
            # Mini carrot pixels tucked into the upper corners.
            painter.setBrush(QColor('#F08A36'))
            painter.drawRect(14, 9, 3, 6); painter.drawRect(113, 9, 3, 6)
            painter.setBrush(QColor('#68AE54'))
            painter.drawRect(13, 6, 2, 4); painter.drawRect(17, 6, 2, 4)
            painter.drawRect(112, 6, 2, 4); painter.drawRect(116, 6, 2, 4)
        elif kind == 'gorilla':
            # Compact knuckle marks replace the wide boulders used previously.
            painter.setBrush(QColor('#687181'))
            painter.drawRect(14, 31, 7, 4); painter.drawRect(109, 31, 7, 4)
            painter.setBrush(QColor('#A2A9B3'))
            painter.drawRect(15, 29, 2, 3); painter.drawRect(18, 28, 2, 4)
            painter.drawRect(110, 28, 2, 4); painter.drawRect(113, 29, 2, 3)
        elif kind == 'dog':
            # Small pixel bones sit against the frame instead of extending it.
            painter.setBrush(QColor('#FFF0C7'))
            for x in (13, 108):
                painter.drawRect(x + 2, 11, 6, 2)
                painter.drawRect(x, 9, 3, 3); painter.drawRect(x, 13, 3, 3)
                painter.drawRect(x + 7, 9, 3, 3); painter.drawRect(x + 7, 13, 3, 3)
        elif kind == 'fox':
            # Small autumn leaf corners complement the fox palette.
            painter.setBrush(QColor('#E97935'))
            painter.drawRect(13, 9, 5, 5); painter.drawRect(112, 9, 5, 5)
            painter.setBrush(QColor('#FFF0D6'))
            painter.drawRect(16, 6, 2, 4); painter.drawRect(112, 6, 2, 4)
        else:  # cat
            # Tiny paw prints keep the classic companion identity.
            painter.setBrush(accent)
            for x in (14, 108):
                painter.drawRect(x + 2, 12, 4, 3)
                painter.drawRect(x, 9, 2, 2); painter.drawRect(x + 4, 8, 2, 2); painter.drawRect(x + 8, 9, 2, 2)


if __name__ == '__main__':
    if sys.platform == 'win32':
        # Give source runs and packaged builds one stable Windows taskbar identity.
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('AzzamQ.DeskPet')
    app = QApplication(sys.argv)
    from app_instance import acquire_instance
    from dashboard import VERSION
    app.setApplicationName('DeskPet')
    app.setApplicationVersion(VERSION)
    app.setWindowIcon(application_icon())
    app.setQuitOnLastWindowClosed(False)
    server = acquire_instance()
    if server is None:
        sys.exit(0)
    window = DesktopPet()
    def activate_existing():
        while server.hasPendingConnections():
            connection = server.nextPendingConnection()
            connection.disconnectFromServer()
            connection.deleteLater()
        window.open_dashboard()
    server.newConnection.connect(activate_existing)
    window.show()
    if '--background' not in sys.argv:
        window.open_dashboard()
    sys.exit(app.exec())
