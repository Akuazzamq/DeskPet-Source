from pathlib import Path
from datetime import datetime
from PySide6.QtCore import Qt, QTimer, QRectF, QSize
from PySide6.QtGui import (QPainter, QColor, QFont, QPixmap, QIcon, QRadialGradient,
    QLinearGradient, QBrush, QPen, QPainterPath)
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QComboBox,
    QCheckBox, QVBoxLayout, QHBoxLayout, QFrame, QGridLayout, QSpinBox, QScrollArea,
    QStackedWidget, QProgressBar)
from pet_engine import PetEngine
from app_icon import application_icon, get_skin_icon, get_type_icon
import startup

VERSION = '0.1.0-beta'


class PetPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pet = PetEngine()
        self.setMinimumSize(260, 220)
        self.frame = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(150)

    def animate(self):
        if not self.isVisible():
            return
        self.frame += 1
        self.pet.idle_frame = (self.frame // 4) % 2
        self.pet.animation_phase = self.frame % 8
        self.pet.tail_frame = (self.frame // 2) % 4
        self.pet.state = 'blink' if self.frame % 30 == 0 else 'idle'
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        w, h = self.width(), self.height()

        # Rounded stage background with ambient radial glow
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        p.setClipPath(path)

        radial = QRadialGradient(w / 2, h / 2 - 10, max(w, h) * 0.65)
        radial.setColorAt(0.0, QColor('#2A1F4E'))
        radial.setColorAt(0.5, QColor('#18142A'))
        radial.setColorAt(1.0, QColor('#100E1C'))
        p.fillRect(self.rect(), radial)

        # Subtle retro pixel grid
        p.setPen(QColor(132, 110, 210, 35))
        for x in range(12, w, 20):
            for y in range(12, h, 20):
                p.drawPoint(x, y)

        # Ambient floor line with glowing mint/purple accent
        floor_y = 194
        p.setPen(QPen(QColor(132, 222, 200, 90), 1.5))
        p.drawLine(20, floor_y, w - 20, floor_y)
        p.setPen(QPen(QColor(185, 160, 255, 40), 1))
        p.drawLine(30, floor_y + 2, w - 30, floor_y + 2)

        # Draw pet sharp
        p.setRenderHint(QPainter.Antialiasing, False)
        p.save()
        p.translate((w - 228) // 2, 18)
        p.scale(2, 2)
        self.pet.draw(p, 0, 0)
        p.restore()
        p.end()


class Dashboard(QWidget):
    def __init__(self, companion):
        super().__init__()
        self.companion = companion
        self.setWindowTitle('DeskPet / Control room')
        self.setWindowIcon(application_icon())
        self.setMinimumSize(780, 600)
        self.resize(900, 780)
        self.setStyleSheet('''
            QWidget {
                color: #EAE9F4;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Consolas, sans-serif;
                font-size: 13px;
            }
            QLabel#muted { color: #A49FBF; font-size: 13px; }
            QLabel#section { color: #84DEC8; font-size: 11px; font-weight: bold; letter-spacing: 1.2px; }
            QLabel#pet_name { color: #FFFFFF; font-size: 15px; font-weight: bold; padding: 4px 0; }
            QLabel#time_display {
                color: #FFFFFF;
                font-family: Consolas;
                font-size: 28px;
                font-weight: bold;
                padding: 4px 0;
            }
            QLabel#version_badge {
                background: rgba(185, 160, 255, 0.12);
                border: 1px solid rgba(185, 160, 255, 0.35);
                border-radius: 10px;
                color: #D6C8FF;
                font-weight: bold;
                padding: 4px 12px;
                font-size: 11px;
            }
            QFrame#card {
                background: rgba(22, 19, 36, 0.92);
                border: 1px solid rgba(138, 115, 210, 0.28);
                border-radius: 12px;
            }
            QFrame#card QLabel, QFrame#card QCheckBox { background: transparent; }
            QComboBox, QSpinBox {
                background: #1B182D;
                border: 1px solid #433B6A;
                border-radius: 8px;
                padding: 8px 12px;
                color: #EAE9F4;
                font-size: 13px;
            }
            QComboBox:hover, QSpinBox:hover {
                border: 1px solid #9D7BFF;
                background: #231F3A;
            }
            QComboBox:focus, QSpinBox:focus {
                border: 1px solid #84DEC8;
            }
            QComboBox QAbstractItemView {
                background: #1B182D;
                border: 1px solid #4D4178;
                border-radius: 6px;
                selection-background-color: #4B3B76;
                selection-color: #FFFFFF;
                padding: 4px;
            }
            QPushButton {
                background: #231F38;
                border: 1px solid #483E70;
                border-radius: 8px;
                padding: 9px 16px;
                color: #DDD9F0;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                border: 1px solid #B9A0FF;
                background: #332B54;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background: #1D1830;
            }
            QPushButton#primary {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #784DE8, stop:1 #A57DFF);
                color: #FFFFFF;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton#primary:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #895EFF, stop:1 #B692FF);
            }
            QPushButton#primary:pressed {
                background: #6A3FD9;
            }
            QPushButton#quit {
                background: rgba(35, 27, 46, 0.7);
                border: 1px solid rgba(138, 115, 210, 0.25);
                border-radius: 8px;
                color: #B4B0D0;
            }
            QPushButton#quit:hover {
                border: 1px solid #FF6584;
                background: rgba(58, 23, 38, 0.8);
                color: #FF8BA7;
            }
            QCheckBox {
                spacing: 10px;
                padding: 5px 0;
                color: #DCD8F0;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 17px;
                height: 17px;
                border-radius: 5px;
                border: 1px solid #5C5287;
                background: #19162A;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #84DEC8;
                background: #221E38;
            }
            QCheckBox::indicator:checked {
                background: #84DEC8;
                border: 2px solid #2B695C;
            }
            QProgressBar {
                background: #19162A;
                border: 1px solid #433B6A;
                border-radius: 4px;
                min-height: 7px;
                max-height: 7px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #84DEC8;
                border-radius: 3px;
            }
        ''')
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 24)
        root.setSpacing(18)

        # Header with styled wordmark & version badge
        header = QHBoxLayout()
        title_img_path = Path(__file__).resolve().parent / 'assets' / 'deskpet_title.png'
        if title_img_path.exists():
            title_pix = QPixmap(str(title_img_path))
            title = QLabel()
            title.setPixmap(title_pix.scaledToHeight(48, Qt.SmoothTransformation))
            header.addWidget(title)
        else:
            logo = QLabel()
            logo.setPixmap(application_icon().pixmap(44, 44))
            header.addWidget(logo)
            title = QLabel('DESKPET')
            title.setObjectName('brand')
            header.addWidget(title)
        header.addStretch()
        version = QLabel(VERSION)
        version.setObjectName('version_badge')
        header.addWidget(version)
        root.addLayout(header)

        intro = QLabel('A little companion. A livelier desktop.')
        intro.setObjectName('muted')
        root.addWidget(intro)

        content = QWidget()
        content.setStyleSheet('background: transparent;')
        content.setMinimumHeight(510)
        body = QHBoxLayout(content)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(22)

        # Left Card: Pet Selection & Preview
        card = QFrame()
        card.setObjectName('card')
        left = QVBoxLayout(card)
        left.setContentsMargins(20, 18, 20, 20)
        left.setSpacing(12)
        label = QLabel('01 / YOUR COMPANION')
        label.setObjectName('section')
        left.addWidget(label)
        self.preview = PetPreview()
        left.addWidget(self.preview, 1)
        self.name = QLabel()
        self.name.setObjectName('pet_name')
        self.name.setAlignment(Qt.AlignCenter)
        left.addWidget(self.name)
        self.types = QComboBox()
        self.types.setIconSize(QSize(22, 22))
        self.skins = QComboBox()
        self.skins.setIconSize(QSize(22, 22))
        for kind in dict.fromkeys(v['type'] for v in companion.pet.pets.values()):
            self.types.addItem(get_type_icon(kind, 22), kind.title(), kind)
        left.addWidget(QLabel('Animal:'))
        left.addWidget(self.types)
        left.addWidget(QLabel('Skin:'))
        left.addWidget(self.skins)
        body.addWidget(card, 1)

        # Right Card: Settings & Time Tools
        right_card = QFrame()
        right_card.setObjectName('card')
        panel = QVBoxLayout(right_card)
        panel.setContentsMargins(22, 18, 22, 20)
        panel.setSpacing(12)

        label = QLabel('02 / MAKE YOURSELF AT HOME')
        label.setObjectName('section')
        panel.addWidget(label)
        self.mode = QComboBox()
        self.mode.addItem('Desktop / stays with you', 'desktop')
        self.mode.addItem('Taskbar / walks & plays', 'taskbar')
        panel.addWidget(QLabel('Position mode:'))
        panel.addWidget(self.mode)
        self.wander = QCheckBox('Walk, run & special actions')
        self.sleep = QCheckBox('Sleep after 3 minutes AFK')
        self.fullscreen = QCheckBox('Hide during fullscreen')
        self.login = QCheckBox('Launch with Windows')
        for check in (self.wander, self.sleep, self.fullscreen, self.login):
            panel.addWidget(check)

        label = QLabel('03 / FOCUS TIME')
        label.setObjectName('section')
        panel.addWidget(label)

        self.time_mode = QComboBox()
        self.time_mode.addItem('Clock / current time', 'clock')
        self.time_mode.addItem('Timer / count down', 'timer')
        self.time_mode.addItem('Stopwatch / count up', 'stopwatch')
        panel.addWidget(self.time_mode)

        panel.addWidget(QLabel('Time bar style:'))
        self.time_bar_style = QComboBox()
        self.time_bar_style.addItem('Classic pixel', 'pixel')
        self.time_bar_style.addItem('Comic pop', 'comic')
        self.time_bar_style.addItem('Cozy wood', 'wood')
        self.time_bar_style.addItem('Cloud dream', 'cloud')
        self.time_bar_style.addItem('Arcade machine', 'arcade')
        panel.addWidget(self.time_bar_style)

        self.time_display = QLabel('00:00:00')
        self.time_display.setObjectName('time_display')
        self.time_display.setAlignment(Qt.AlignCenter)
        panel.addWidget(self.time_display)

        self.time_progress = QProgressBar()
        self.time_progress.setTextVisible(False)
        self.time_progress.setRange(0, 1000)
        panel.addWidget(self.time_progress)

        self.time_pages = QStackedWidget()
        clock_page = QWidget()
        clock_layout = QVBoxLayout(clock_page)
        clock_layout.setContentsMargins(0, 0, 0, 0)
        clock_note = QLabel('The current time is shown above your companion.')
        clock_note.setObjectName('muted')
        clock_note.setWordWrap(True)
        clock_layout.addWidget(clock_note)
        self.time_pages.addWidget(clock_page)

        timer_page = QWidget()
        timer_layout = QVBoxLayout(timer_page)
        timer_layout.setContentsMargins(0, 0, 0, 0)
        timer_layout.setSpacing(8)
        self.timer_preset = QComboBox()
        for label_text, value in (
            ('Quick break - 5 min', 5), ('Short focus - 15 min', 15),
            ('Pomodoro - 25 min', 25), ('Deep focus - 45 min', 45),
            ('Long focus - 60 min', 60), ('Custom duration', 0)):
            self.timer_preset.addItem(label_text, value)
        self.timer_preset.setCurrentIndex(2)
        timer_layout.addWidget(self.timer_preset)
        timerline = QHBoxLayout()
        self.minutes = QSpinBox()
        self.minutes.setRange(1, 1440)
        self.minutes.setValue(25)
        self.minutes.setSuffix(' min')
        timerline.addWidget(self.minutes)
        self.timer_start = QPushButton('Start timer')
        self.timer_start.setObjectName('primary')
        self.timer_start.clicked.connect(self.start_timer)
        timerline.addWidget(self.timer_start)
        timer_layout.addLayout(timerline)
        timer_buttons = QHBoxLayout()
        self.timer_toggle = QPushButton('Pause')
        self.timer_toggle.clicked.connect(self.toggle_timer)
        self.timer_reset = QPushButton('Reset')
        self.timer_reset.clicked.connect(self.reset_timer)
        timer_buttons.addWidget(self.timer_toggle)
        timer_buttons.addWidget(self.timer_reset)
        timer_layout.addLayout(timer_buttons)
        self.time_pages.addWidget(timer_page)

        stopwatch_page = QWidget()
        stopwatch_layout = QHBoxLayout(stopwatch_page)
        stopwatch_layout.setContentsMargins(0, 0, 0, 0)
        self.stopwatch_toggle = QPushButton('Start stopwatch')
        self.stopwatch_toggle.setObjectName('primary')
        self.stopwatch_toggle.clicked.connect(self.toggle_stopwatch)
        self.stopwatch_reset = QPushButton('Reset')
        self.stopwatch_reset.clicked.connect(self.reset_stopwatch)
        stopwatch_layout.addWidget(self.stopwatch_toggle)
        stopwatch_layout.addWidget(self.stopwatch_reset)
        self.time_pages.addWidget(stopwatch_page)
        panel.addWidget(self.time_pages)

        self.status = QLabel('Ready when you are.')
        self.status.setObjectName('muted')
        self.status.setWordWrap(True)
        panel.addWidget(self.status)
        panel.addStretch()

        self.show_button = QPushButton('> Show companion')
        self.show_button.setObjectName('primary')
        self.show_button.clicked.connect(companion.show_pet)
        panel.addWidget(self.show_button)
        self.pause = QPushButton()
        self.pause.clicked.connect(self.toggle_pause)
        panel.addWidget(self.pause)
        body.addWidget(right_card, 1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet('background: transparent;')
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        hint = QLabel('Drag your pet to move it. Right-click for more controls.\nClosing this dashboard keeps your companion running.')
        hint.setObjectName('muted')
        hint.setWordWrap(True)
        root.addWidget(hint)

        footer = QHBoxLayout()
        footer_brand = QLabel('BY AZZAMQ  /  PIXEL COMPANIONS')
        footer_brand.setStyleSheet('color: #7E779E; font-size: 11px; font-weight: bold; letter-spacing: 1px;')
        footer.addWidget(footer_brand)
        footer.addStretch()
        quit_button = QPushButton('Quit DeskPet')
        quit_button.setObjectName('quit')
        quit_button.clicked.connect(QApplication.quit)
        footer.addWidget(quit_button)
        root.addLayout(footer)

        self.types.currentIndexChanged.connect(self.change_type)
        self.skins.currentIndexChanged.connect(self.change_skin)
        self.mode.currentIndexChanged.connect(self.change_mode)
        self.time_mode.currentIndexChanged.connect(self.change_time_mode)
        self.time_bar_style.currentIndexChanged.connect(self.change_time_bar_style)
        self.timer_preset.currentIndexChanged.connect(self.apply_timer_preset)
        self.minutes.valueChanged.connect(self.custom_minutes_changed)
        self.wander.toggled.connect(lambda value: self.setting('wander', value))
        self.sleep.toggled.connect(lambda value: self.setting('sleep_enabled', value))
        self.fullscreen.toggled.connect(self.fullscreen_changed)
        self.login.toggled.connect(self.login_changed)
        for control in self.findChildren(QPushButton) + self.findChildren(QComboBox) + self.findChildren(QSpinBox):
            control.setMinimumHeight(38)
        self.status.setMinimumHeight(44)
        self.time_refresh = QTimer(self)
        self.time_refresh.timeout.connect(self.refresh_time_controls)
        self.time_refresh.start(250)
        self.sync()

    def paintEvent(self, event):
        # Deep cosmic ambient background matching the DESKPET palette
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        w, h = self.width(), self.height()

        # Smooth midnight gradient
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor('#0D0B18'))
        grad.setColorAt(0.4, QColor('#141026'))
        grad.setColorAt(1.0, QColor('#1B1435'))
        p.fillRect(self.rect(), grad)

        # Ambient soft glow behind header
        glow = QRadialGradient(160, 50, 320)
        glow.setColorAt(0.0, QColor(140, 95, 245, 38))
        glow.setColorAt(1.0, QColor(13, 11, 24, 0))
        p.fillRect(QRectF(0, 0, w, 200), glow)

        # Ambient soft glow bottom-right
        glow_br = QRadialGradient(w - 100, h - 100, 300)
        glow_br.setColorAt(0.0, QColor(132, 222, 200, 18))
        glow_br.setColorAt(1.0, QColor(27, 20, 53, 0))
        p.fillRect(QRectF(w - 400, h - 400, 400, 400), glow_br)

        # Very subtle grid dots for clean retro-depth
        p.setPen(QColor(165, 145, 235, 15))
        for gx in range(24, w, 28):
            for gy in range(24, h, 28):
                p.drawPoint(gx, gy)
        p.end()

    def sync(self):
        c = self.companion
        widgets = (self.types, self.skins, self.mode, self.time_mode, self.time_bar_style,
                   self.wander, self.sleep, self.fullscreen, self.login)
        for widget in widgets: widget.blockSignals(True)
        self.types.setCurrentIndex(self.types.findData(c.pet.get_pet_type()))
        self.skins.clear()
        for key, data in c.pet.pets.items():
            if data['type'] == c.pet.get_pet_type():
                self.skins.addItem(get_skin_icon(key, 22), data['name'], key)
        self.skins.setCurrentIndex(self.skins.findData(c.pet.skin))
        self.mode.setCurrentIndex(self.mode.findData(c.mode))
        self.time_mode.setCurrentIndex(self.time_mode.findData(c.time_tools.mode))
        self.time_bar_style.setCurrentIndex(self.time_bar_style.findData(c.time_bar_style))
        self.time_pages.setCurrentIndex(max(0, self.time_mode.currentIndex()))
        self.wander.setChecked(c.behavior.wander); self.wander.setEnabled(c.mode == 'taskbar')
        self.sleep.setChecked(c.behavior.sleep_enabled)
        self.fullscreen.setChecked(c.hide_fullscreen)
        self.login.setChecked(startup.enabled())
        for widget in widgets: widget.blockSignals(False)
        self.preview.pet.set_skin(c.pet.skin); self.preview.update()
        self.name.setText(c.pet.pets[c.pet.skin]['name'])
        self.pause.setText('Resume animations' if c.behavior.paused else 'Pause animations')
        self.refresh_time_controls()

    def change_type(self):
        self.companion.change_type(self.types.currentData()); self.sync()

    def change_skin(self):
        if self.skins.currentData(): self.companion.change_pet(self.skins.currentData()); self.sync()

    def change_mode(self):
        self.companion.set_mode(self.mode.currentData()); self.sync()

    def change_time_mode(self):
        mode = self.time_mode.currentData()
        if not mode:
            return
        self.companion.select_time_mode(mode)
        self.time_pages.setCurrentIndex(self.time_mode.currentIndex())
        self.refresh_time_controls()

    def change_time_bar_style(self):
        style = self.time_bar_style.currentData()
        if style:
            self.companion.select_time_bar_style(style)
            names = {'pixel': 'Classic pixel', 'comic': 'Comic pop',
                     'wood': 'Cozy wood', 'cloud': 'Cloud dream',
                     'arcade': 'Arcade machine'}
            self.status.setText(f'{names.get(style, "Time bar")} selected.')

    def apply_timer_preset(self):
        minutes = self.timer_preset.currentData()
        if minutes:
            self.minutes.setValue(minutes)

    def custom_minutes_changed(self, minutes):
        if self.timer_preset.currentData() not in (0, minutes):
            self.timer_preset.setCurrentIndex(self.timer_preset.findData(0))

    def setting(self, key, value):
        setattr(self.companion.behavior, key, value); self.companion.save_settings()

    def fullscreen_changed(self, value):
        self.companion.hide_fullscreen = value; self.companion.save_settings()

    def login_changed(self, value):
        self.companion.toggle_startup(value); self.sync()

    def toggle_pause(self):
        self.companion.toggle_pause(not self.companion.behavior.paused); self.sync()

    def start_timer(self):
        self.companion.time_tools.start_timer(self.minutes.value() * 60)
        self.time_mode.setCurrentIndex(self.time_mode.findData('timer'))
        self.companion.show_pet()
        self.status.setText(f'Focus timer started for {self.minutes.value()} minutes.')
        self.refresh_time_controls()

    def toggle_timer(self):
        tools = self.companion.time_tools
        if tools.finished:
            return
        tools.mode = 'timer'
        tools.toggle_timer()
        self.refresh_time_controls()

    def reset_timer(self):
        self.companion.time_tools.mode = 'timer'
        self.companion.time_tools.reset_timer()
        self.status.setText('Timer reset and ready.')
        self.refresh_time_controls()

    def toggle_stopwatch(self):
        self.companion.time_tools.toggle_stopwatch()
        self.time_mode.setCurrentIndex(self.time_mode.findData('stopwatch'))
        self.refresh_time_controls()

    def reset_stopwatch(self):
        self.companion.time_tools.mode = 'stopwatch'
        self.companion.time_tools.reset_stopwatch()
        self.status.setText('Stopwatch reset and ready.')
        self.refresh_time_controls()

    def refresh_time_controls(self):
        if not self.isVisible():
            return
        tools = self.companion.time_tools
        mode = tools.mode
        if mode == 'clock':
            self.time_display.setText(datetime.now().strftime('%H:%M:%S'))
            self.time_progress.hide()
            self.status.setText('Clock is visible above your companion.')
        elif mode == 'timer':
            self.time_progress.show()
            label, value = tools.display()
            self.time_display.setText(value)
            self.time_progress.setRange(0, 1000)
            remaining = max(0, tools.deadline - tools.clock()) if tools.deadline is not None else tools.remaining
            progress = 1 - remaining / max(1, tools.duration)
            self.time_progress.setValue(round(max(0, min(1, progress)) * 1000))
            running = tools.deadline is not None
            used = running or tools.finished or tools.remaining < tools.duration
            self.timer_start.setText('Restart timer' if running or tools.finished else 'Start timer')
            self.timer_toggle.setText('Pause' if running else 'Resume' if used else 'Pause / resume')
            self.timer_toggle.setEnabled(not tools.finished and used)
            self.status.setText('Time is up!' if tools.finished else label.title())
        else:
            self.time_progress.hide()
            self.time_display.setText(tools.format_seconds(tools.stopwatch_seconds()))
            self.time_progress.setRange(0, 0)
            self.stopwatch_toggle.setText('Pause' if tools.started is not None else
                                          'Resume' if tools.elapsed else 'Start stopwatch')
            self.status.setText('Stopwatch running.' if tools.started is not None else 'Stopwatch ready.')
        self.companion.update()

    def showEvent(self, event):
        self.sync(); super().showEvent(event)

    def closeEvent(self, event):
        self.companion.save_settings()
        self.hide(); event.ignore()
