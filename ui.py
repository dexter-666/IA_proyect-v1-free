"""ui.py — 100% Custom Gold-Themed Dynamic Bento PyQt6 User Interface for JARVIS.

Fully optimized HUD layouts:
- Background WebGL reactive Particle Orb covering the screen.
- Floating transparent digital clock at the top-right corner.
- Organized Bento grid dashboard aligned perfectly at the bottom half.
- Centered speech captions at the bottom.
"""
from __future__ import annotations
import sys
import os
import json
import psutil
from pathlib import Path
from datetime import datetime, timezone, timedelta

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QTextEdit, 
    QListWidget, QListWidgetItem, QProgressBar, QDialog, QMessageBox,
    QComboBox, QCheckBox, QGraphicsDropShadowEffect, QTabWidget
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, pyqtSlot, QObject, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QMouseEvent
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

try:
    import qtawesome as qta
    HAS_QTA = True
except ImportError:
    HAS_QTA = False

# Active Timezone Peru (UTC-5)
_BA_TZ = timezone(timedelta(hours=-5))

# Themes Configuration
THEMES = {
    "cyan": {
        "PRI": "#00d4ff", "PRI_DIM": "#005f77", "BG": "#050c14", 
        "PANEL": "rgba(10, 22, 32, 0.7)", "BORDER": "rgba(0, 212, 255, 0.45)", "TEXT": "#7aeeff"
    },
    "green": {
        "PRI": "#00ff88", "PRI_DIM": "#006633", "BG": "#040e08", 
        "PANEL": "rgba(8, 26, 16, 0.7)", "BORDER": "rgba(0, 255, 136, 0.45)", "TEXT": "#7affcc"
    },
    "red": {
        "PRI": "#ff3b30", "PRI_DIM": "#7a1a15", "BG": "#0e0404", 
        "PANEL": "rgba(26, 8, 8, 0.7)", "BORDER": "rgba(255, 59, 48, 0.45)", "TEXT": "#ffaaaa"
    },
    "purple": {
        "PRI": "#a855f7", "PRI_DIM": "#5b21b6", "BG": "#07030f", 
        "PANEL": "rgba(15, 6, 24, 0.7)", "BORDER": "rgba(168, 85, 247, 0.45)", "TEXT": "#c084fc"
    },
    "gold": {
        "PRI": "#f59e0b", "PRI_DIM": "#78350f", "BG": "#0f0a02", 
        "PANEL": "rgba(35, 28, 10, 0.70)", "BORDER": "rgba(245, 158, 11, 0.45)", "TEXT": "#fde68a"
    },
    "white": {
        "PRI": "#e2e8f0", "PRI_DIM": "#64748b", "BG": "#050a14", 
        "PANEL": "rgba(12, 22, 38, 0.7)", "BORDER": "rgba(226, 232, 240, 0.45)", "TEXT": "#cbd5e1"
    }
}

# Theme Tokens
C_PRI = "#f59e0b"
C_PRI_DIM = "#78350f"
C_BG = "#0f0a02"
C_PANEL = "rgba(35, 28, 10, 0.70)"
C_BORDER = "rgba(245, 158, 11, 0.45)"
C_TEXT = "#fde68a"

GREEN = "#00ff88"
RED = "#ff3b30"

def apply_theme_tokens(theme_name: str):
    global C_PRI, C_PRI_DIM, C_BG, C_PANEL, C_BORDER, C_TEXT
    t = THEMES.get(theme_name.lower(), THEMES["gold"])
    C_PRI = t["PRI"]
    C_PRI_DIM = t["PRI_DIM"]
    C_BG = t["BG"]
    C_PANEL = t["PANEL"]
    C_BORDER = t["BORDER"]
    C_TEXT = t["TEXT"]

try:
    from memory.config_manager import load_api_keys
    _theme_name = load_api_keys().get("jarvis_theme", "gold")
    apply_theme_tokens(_theme_name)
except Exception:
    apply_theme_tokens("gold")


class WebBridge(QObject):
    def __init__(self, orb):
        super().__init__()
        self.orb = orb

    @pyqtSlot()
    def toggle_mute(self):
        if self.orb.ui:
            self.orb.ui._win._toggle_mute()

    @pyqtSlot()
    def request_theme(self):
        QTimer.singleShot(0, self.orb.sync_theme)


class CustomParticleOrb(QWidget):
    audio_signal = pyqtSignal(float)
    state_signal = pyqtSignal(str)
    theme_signal = pyqtSignal()

    def __init__(self, ui, parent=None):
        super().__init__(parent)
        self.ui = ui
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.web_view = QWebEngineView(self)
        self.web_view.setStyleSheet("background: transparent;")
        self.web_view.page().setBackgroundColor(Qt.GlobalColor.transparent)
        
        try:
            from PyQt6.QtWebEngineCore import QWebEngineSettings
            settings = self.web_view.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, False)
        except Exception:
            pass
            
        self.channel = QWebChannel()
        self.bridge = WebBridge(self)
        self.channel.registerObject("pyBridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        
        import sys
        if getattr(sys, "frozen", False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = (Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent)
        sphere_path = base_dir / "assets" / "sphere.html"
        self.web_view.setUrl(QUrl.fromLocalFile(str(sphere_path.absolute())))
        
        layout.addWidget(self.web_view)
        self.setLayout(layout)
        
        self.audio_signal.connect(self._safe_set_audio)
        self.state_signal.connect(self._safe_set_state)
        self.theme_signal.connect(self._safe_sync_theme)
        self.web_view.loadFinished.connect(self._on_load_finished)
        
    def _on_load_finished(self, ok):
        if ok:
            self.sync_theme()
            self.set_state("MUTED" if self.ui.muted else "LISTENING")

    def sync_theme(self):
        self.theme_signal.emit()

    def set_audio(self, level: float):
        self.audio_signal.emit(level)
        
    def set_state(self, state: str):
        self.state_signal.emit(state)

    def _safe_sync_theme(self):
        colors = {
            'PRI': C_PRI,
            'PRI_DIM': C_PRI_DIM,
            'TEXT': C_TEXT,
            'BG': C_BG
        }
        js_code = f"if (window.setThemeColors) window.setThemeColors({json.dumps(colors)});"
        self.web_view.page().runJavaScript(js_code)

    def _safe_set_audio(self, level: float):
        js_code = f"if (window.updateVolume) window.updateVolume({level});"
        self.web_view.page().runJavaScript(js_code)

    def _safe_set_state(self, state: str):
        js_code = f"if (window.updateState) window.updateState('{state}');"
        self.web_view.page().runJavaScript(js_code)


class ClockWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ClockWidget")
        self.update_style()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.lbl_time = QLabel("12:00:00")
        font_t = QFont("Century Gothic", 24, QFont.Weight.Bold)
        font_t.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.0)
        self.lbl_time.setFont(font_t)
        self.lbl_time.setStyleSheet("color: white; border: none; background: transparent;")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.lbl_time)
        
        self.lbl_date = QLabel("Monday, 24 May 2026")
        self.lbl_date.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.lbl_date)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)
        self.tick()
        
    def tick(self):
        now = datetime.now(_BA_TZ)
        self.lbl_time.setText(now.strftime("%I:%M:%S %p"))
        self.lbl_date.setText(now.strftime("%A, %d %B %Y"))
        
    def update_style(self):
        # Completely borderless and transparent for elegant floating style
        self.setStyleSheet("""
            QWidget#ClockWidget {
                background: transparent;
                border: none;
            }
        """)
        if hasattr(self, "lbl_date"):
            self.lbl_date.setStyleSheet(f"font-size: 11px; letter-spacing: 1px; color: {C_PRI}; border: none; background: transparent; font-weight: bold;")


class WeatherWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WeatherWidget")
        self.update_style()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        
        header = QHBoxLayout()
        lbl_icon = QLabel()
        if HAS_QTA:
            lbl_icon.setPixmap(qta.icon('fa5s.cloud-sun', color=C_PRI).pixmap(18, 18))
        header.addWidget(lbl_icon)
        
        self.lbl_title = QLabel("WEATHER REPORT")
        header.addWidget(self.lbl_title)
        header.addStretch()
        layout.addLayout(header)
        
        info = QHBoxLayout()
        self.lbl_temp = QLabel("18°C")
        self.lbl_temp.setStyleSheet("font-size: 20px; font-weight: bold; border: none; background: transparent; color: white;")
        info.addWidget(self.lbl_temp)
        
        self.lbl_desc = QLabel("Parcialmente Nublado")
        info.addWidget(self.lbl_desc)
        info.addStretch()
        layout.addLayout(info)
        
        details = QHBoxLayout()
        self.lbl_humidity = QLabel("Humedad: 82%")
        self.lbl_humidity.setStyleSheet("font-size: 10px; color: #94a3b8; border: none; background: transparent;")
        self.lbl_wind = QLabel("Viento: 12 km/h")
        self.lbl_wind.setStyleSheet("font-size: 10px; color: #94a3b8; border: none; background: transparent;")
        
        details.addWidget(self.lbl_humidity)
        details.addWidget(self.lbl_wind)
        details.addStretch()
        layout.addLayout(details)
        
    def update_style(self):
        self.setStyleSheet(f"""
            QWidget#WeatherWidget {{
                background: {C_PANEL};
                border: 1.5px solid {C_BORDER};
                border-radius: 12px;
            }}
        """)
        if hasattr(self, "lbl_title"):
            self.lbl_title.setStyleSheet(f"font-weight: bold; font-size: 11px; letter-spacing: 2px; color: {C_PRI}; border: none; background: transparent;")
            self.lbl_desc.setStyleSheet(f"font-size: 11px; color: {C_TEXT}; border: none; background: transparent;")


class SpotifyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SpotifyWidget")
        self.update_style()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        header = QHBoxLayout()
        self.lbl_logo = QLabel()
        if HAS_QTA:
            self.lbl_logo.setPixmap(qta.icon('fa5b.spotify', color='#1DB954').pixmap(18, 18))
        else:
            self.lbl_logo.setText("🎵")
        header.addWidget(self.lbl_logo)
        
        self.lbl_title = QLabel("SPOTIFY CONTROL")
        header.addWidget(self.lbl_title)
        header.addStretch()
        layout.addLayout(header)
        
        self.lbl_track = QLabel("Not Playing")
        self.lbl_track.setStyleSheet("font-size: 13px; font-weight: bold; border: none; background: transparent; color: white;")
        self.lbl_artist = QLabel("Awaiting tracks...")
        layout.addWidget(self.lbl_track)
        layout.addWidget(self.lbl_artist)
        
        controls = QHBoxLayout()
        self.btn_shuffle = QPushButton()
        self.btn_prev = QPushButton()
        self.btn_play = QPushButton()
        self.btn_next = QPushButton()
        self.btn_heart = QPushButton()
        
        self.buttons_list = [
            (self.btn_shuffle, 'fa5s.random', C_PRI_DIM),
            (self.btn_prev, 'fa5s.step-backward', '#ffffff'),
            (self.btn_play, 'fa5s.play', '#ffffff'),
            (self.btn_next, 'fa5s.step-forward', '#ffffff'),
            (self.btn_heart, 'fa5s.heart', RED)
        ]
        
        for btn, icon, clr in self.buttons_list:
            if HAS_QTA:
                btn.setIcon(qta.icon(icon, color=clr))
            btn.setFixedSize(30, 30)
            controls.addWidget(btn)
            
        layout.addLayout(controls)
        
        self.btn_play.clicked.connect(lambda: self._press("playpause"))
        self.btn_prev.clicked.connect(lambda: self._press("prevtrack"))
        self.btn_next.clicked.connect(lambda: self._press("nexttrack"))
        
    def _press(self, key):
        try:
            import pyautogui
            pyautogui.press(key)
        except Exception:
            pass

    def update_style(self):
        self.setStyleSheet(f"""
            QWidget#SpotifyWidget {{
                background: {C_PANEL};
                border: 1.5px solid {C_BORDER};
                border-radius: 12px;
            }}
        """)
        if hasattr(self, "lbl_title"):
            self.lbl_title.setStyleSheet(f"font-weight: bold; font-size: 11px; letter-spacing: 2px; color: {C_PRI}; border: none; background: transparent;")
            self.lbl_artist.setStyleSheet(f"font-size: 11px; color: {C_PRI_DIM}; border: none; background: transparent;")
            for btn, icon, clr in self.buttons_list:
                btn.setStyleSheet(f"QPushButton {{ background: rgba(245,158,11,0.08); border: 1px solid {C_BORDER}; border-radius: 15px; }} QPushButton:hover {{ background: rgba(245,158,11,0.2); }}")


class SystemWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SystemWidget")
        self.update_style()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        header = QHBoxLayout()
        lbl_icon = QLabel()
        if HAS_QTA:
            lbl_icon.setPixmap(qta.icon('fa5s.bolt', color=C_PRI).pixmap(18, 18))
        header.addWidget(lbl_icon)
        
        self.lbl_title = QLabel("SYSTEM GAUGES")
        header.addWidget(self.lbl_title)
        header.addStretch()
        layout.addLayout(header)
        
        self.cpu_bar = QProgressBar()
        self.ram_bar = QProgressBar()
        self.ram_bar.mousePressEvent = self.optimize_ram_click
        self.ram_bar.setToolTip("Click to clean and optimize physical RAM usage, sir.")
        
        self.bars = [(self.cpu_bar, "CPU Status"), (self.ram_bar, "RAM Status (Click to optimize)")]
        for bar, label in self.bars:
            lbl = QLabel(label)
            lbl.setStyleSheet(f"font-size: 10px; color: {C_PRI_DIM}; border: none; background: transparent;")
            layout.addWidget(lbl)
            bar.setTextVisible(True)
            layout.addWidget(bar)
            
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)
        self._ram_opt_counter = 0
        self.update_stats()
        
    def optimize_ram_click(self, event):
        self.optimize_ram()
        QMessageBox.information(self, "RAM Cleaned", "JARVIS physical RAM memory optimized, sir.")

    def optimize_ram(self):
        import gc
        gc.collect()
        try:
            import ctypes
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.psapi.EmptyWorkingSet(handle)
        except Exception:
            pass

    def update_stats(self):
        try:
            self.cpu_bar.setValue(int(psutil.cpu_percent()))
            self.ram_bar.setValue(int(psutil.virtual_memory().percent))
        except Exception:
            pass
        self._ram_opt_counter += 1
        if self._ram_opt_counter >= 60:
            self._ram_opt_counter = 0
            self.optimize_ram()

    def update_style(self):
        self.setStyleSheet(f"""
            QWidget#SystemWidget {{
                background: {C_PANEL};
                border: 1.5px solid {C_BORDER};
                border-radius: 12px;
            }}
        """)
        if hasattr(self, "lbl_title"):
            self.lbl_title.setStyleSheet(f"font-weight: bold; font-size: 11px; letter-spacing: 2px; color: {C_PRI}; border: none; background: transparent;")
            for bar, label in self.bars:
                bar.setStyleSheet(f"""
                    QProgressBar {{
                        border: 1px solid {C_BORDER};
                        border-radius: 6px;
                        text-align: center;
                        background: transparent;
                        color: white;
                        height: 14px;
                    }}
                    QProgressBar::chunk {{
                        background-color: {C_PRI};
                        border-radius: 5px;
                    }}
                """)


class TodoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TodoWidget")
        self.update_style()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        header = QHBoxLayout()
        lbl_icon = QLabel()
        if HAS_QTA:
            lbl_icon.setPixmap(qta.icon('fa5s.check-circle', color=C_PRI).pixmap(18, 18))
        header.addWidget(lbl_icon)
        
        self.lbl_title = QLabel("TODOS")
        header.addWidget(self.lbl_title)
        header.addStretch()
        layout.addLayout(header)
        
        inp_layout = QHBoxLayout()
        self.txt_task = QLineEdit()
        self.txt_task.setPlaceholderText("New chore...")
        inp_layout.addWidget(self.txt_task)
        
        self.btn_add = QPushButton("+")
        inp_layout.addWidget(self.btn_add)
        layout.addLayout(inp_layout)
        
        self.lst_todo = QListWidget()
        self.lst_todo.setStyleSheet("QListWidget { border: none; background: transparent; } QListWidget::item { padding: 4px; color: white; }")
        layout.addWidget(self.lst_todo)
        
        self.btn_add.clicked.connect(self.add_task)
        self.txt_task.returnPressed.connect(self.add_task)
        
    def add_task(self):
        text = self.txt_task.text().strip()
        if text:
            item = QListWidgetItem(text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.lst_todo.addItem(item)
            self.txt_task.clear()

    def update_style(self):
        self.setStyleSheet(f"""
            QWidget#TodoWidget {{
                background: {C_PANEL};
                border: 1.5px solid {C_BORDER};
                border-radius: 12px;
            }}
        """)
        if hasattr(self, "lbl_title"):
            self.lbl_title.setStyleSheet(f"font-weight: bold; font-size: 11px; letter-spacing: 2px; color: {C_PRI}; border: none; background: transparent;")
            self.txt_task.setStyleSheet(f"QLineEdit {{ background: rgba(0,0,0,0.3); border: 1px solid {C_BORDER}; border-radius: 6px; padding: 4px; color: white; }}")
            self.btn_add.setStyleSheet(f"QPushButton {{ background: {C_PRI}; color: black; font-weight: bold; border-radius: 6px; padding: 4px 10px; }}")


class NotesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NotesWidget")
        self.update_style()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        header = QHBoxLayout()
        lbl_icon = QLabel()
        if HAS_QTA:
            lbl_icon.setPixmap(qta.icon('fa5s.sticky-note', color=C_PRI).pixmap(18, 18))
        header.addWidget(lbl_icon)
        
        self.lbl_title = QLabel("PAD NOTES")
        header.addWidget(self.lbl_title)
        header.addStretch()
        layout.addLayout(header)
        
        self.txt_notes = QTextEdit()
        self.txt_notes.setPlaceholderText("Write details...")
        layout.addWidget(self.txt_notes)

    def update_style(self):
        self.setStyleSheet(f"""
            QWidget#NotesWidget {{
                background: {C_PANEL};
                border: 1.5px solid {C_BORDER};
                border-radius: 12px;
            }}
        """)
        if hasattr(self, "lbl_title"):
            self.lbl_title.setStyleSheet(f"font-weight: bold; font-size: 11px; letter-spacing: 2px; color: {C_PRI}; border: none; background: transparent;")
            self.txt_notes.setStyleSheet(f"QTextEdit {{ border: none; background: rgba(0,0,0,0.2); border-radius: 6px; padding: 6px; color: white; }}")


class FileDropZone(QWidget):
    fileDropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.update_style()
        layout = QVBoxLayout(self)
        self.lbl = QLabel("Drop File Trigger")
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setStyleSheet("border: none; background: transparent; font-weight: bold; color: white;")
        layout.addWidget(self.lbl)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(f"QWidget {{ background: rgba(245,158,11,0.15); border: 2px dashed {C_PRI}; border-radius: 10px; }}")

    def dragLeaveEvent(self, event):
        self.update_style()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.exists(path):
                self.fileDropped.emit(path)
                break
        self.dragLeaveEvent(None)

    def update_style(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: rgba(0,0,0,0.25);
                border: 1.5px dashed {C_BORDER};
                border-radius: 10px;
            }}
        """)


class FilesPanel(QWidget):
    def __init__(self, ui, parent=None):
        super().__init__(parent)
        self.ui = ui
        self.setObjectName("FilesPanel")
        self.update_style()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        header = QHBoxLayout()
        lbl_icon = QLabel()
        if HAS_QTA:
            lbl_icon.setPixmap(qta.icon('fa5s.folder-open', color=C_PRI).pixmap(18, 18))
        header.addWidget(lbl_icon)
        
        self.lbl_title = QLabel("FILES DROP")
        header.addWidget(self.lbl_title)
        header.addStretch()
        layout.addLayout(header)
        
        self.drop_zone = FileDropZone()
        self.drop_zone.fileDropped.connect(self.on_file_dropped)
        layout.addWidget(self.drop_zone)
        
        self.lbl_current = QLabel("Ready for drops.")
        layout.addWidget(self.lbl_current)
        
    def on_file_dropped(self, path):
        self.ui.current_file = path
        name = os.path.basename(path)
        self.lbl_current.setText(f"Active: {name}")
        self.ui.write_log(f"📁 Drops linked: {name}")

    def update_style(self):
        self.setStyleSheet(f"""
            QWidget#FilesPanel {{
                background: {C_PANEL};
                border: 1.5px solid {C_BORDER};
                border-radius: 12px;
            }}
        """)
        if hasattr(self, "lbl_title"):
            self.lbl_title.setStyleSheet(f"font-weight: bold; font-size: 11px; letter-spacing: 2px; color: {C_PRI}; border: none; background: transparent;")
            self.lbl_current.setStyleSheet(f"font-size: 10px; color: {C_PRI_DIM}; border: none; background: transparent;")
            self.drop_zone.update_style()


class DeviceSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JARVIS Settings Configuration Control")
        self.resize(500, 480)
        self.update_style()
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        title_lbl = QLabel("<h2>System Master Configurations</h2>")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)
        
        # QTabWidget for compact representation (saves space on laptops)
        self.tabs = QTabWidget()
        self.tabs.setObjectName("SettingsTabs")
        
        # TAB 1: APIs & Provider
        tab_api = QWidget()
        lay_api = QVBoxLayout(tab_api)
        lay_api.setSpacing(6)
        
        lay_api.addWidget(QLabel("Gemini API Key:"))
        self.inp_gemini = QLineEdit()
        self.inp_gemini.setEchoMode(QLineEdit.EchoMode.Password)
        lay_api.addWidget(self.inp_gemini)
        
        lay_api.addWidget(QLabel("OpenRouter API Key:"))
        self.inp_openrouter = QLineEdit()
        self.inp_openrouter.setEchoMode(QLineEdit.EchoMode.Password)
        lay_api.addWidget(self.inp_openrouter)
        
        lay_api.addWidget(QLabel("AI Provider (Proveedor Principal):"))
        self.cmb_ai_provider = QComboBox()
        self.cmb_ai_provider.addItem("Google Gemini (Default)", "gemini")
        self.cmb_ai_provider.addItem("OpenRouter API", "openrouter")
        lay_api.addWidget(self.cmb_ai_provider)
        
        lay_api.addWidget(QLabel("LLM Engine (Free Version Restricted):"))
        self.cmb_llm = QComboBox()
        self.cmb_llm.addItem("Gemini 1.5 Flash (Basic/Free)", "gemini-1.5-flash")
        self.cmb_llm.addItem("Gemini 2.0 Flash Lite (Optimized)", "gemini-2.0-flash-lite")
        lay_api.addWidget(self.cmb_llm)
        lay_api.addStretch()
        
        # TAB 2: Audio & Local Voice
        tab_audio = QWidget()
        lay_audio = QVBoxLayout(tab_audio)
        lay_audio.setSpacing(6)
        
        lay_audio.addWidget(QLabel("Microphone Input Device:"))
        self.cmb_mic = QComboBox()
        lay_audio.addWidget(self.cmb_mic)
        
        lay_audio.addWidget(QLabel("Speaker Output Device:"))
        self.cmb_speaker = QComboBox()
        lay_audio.addWidget(self.cmb_speaker)
        
        lay_audio.addWidget(QLabel("Active Voice Model:"))
        self.cmb_voice = QComboBox()
        self.voices = [
            ("Aoede", "Femenina (Cálida y sofisticada ✨)"),
            ("Kore", "Femenina (Suave y precisa)"),
            ("Leda", "Femenina (Natural y fluida)"),
            ("Zephyr", "Femenina (Dinámica y expresiva)"),
            ("Charon", "Masculina (Profunda y seria)"),
            ("Puck", "Masculina (Ágil y versátil)"),
            ("Fenrir", "Masculina (Grave y autoritaria)"),
            ("Orus", "Masculina (Clásica y equilibrada)")
        ]
        for val, desc in self.voices:
            self.cmb_voice.addItem(desc, val)
        lay_audio.addWidget(self.cmb_voice)
        
        lay_audio.addWidget(QLabel("Local AI Integration (Vosk Wake Word):"))
        self.btn_download_vosk = QPushButton("Descargar Modelo IA Local (Vosk)")
        self.btn_download_vosk.setStyleSheet("background-color: #f59e0b; color: black; font-weight: bold;")
        self.btn_download_vosk.clicked.connect(self._manual_download_vosk)
        lay_audio.addWidget(self.btn_download_vosk)
        lay_audio.addStretch()
        
        # TAB 3: Theme & Integration (Spotify)
        tab_other = QWidget()
        lay_other = QVBoxLayout(tab_other)
        lay_other.setSpacing(6)
        
        lay_other.addWidget(QLabel("Theme Palette Scheme:"))
        self.cmb_theme = QComboBox()
        for k in THEMES.keys():
            self.cmb_theme.addItem(k.upper(), k)
        lay_other.addWidget(self.cmb_theme)
        
        self.chk_gpu = QCheckBox("Enable GPU Rendering Acceleration")
        lay_other.addWidget(self.chk_gpu)
        
        lay_other.addWidget(QLabel("<h3>Spotify Developer Integration</h3>"))
        
        self.spotify_id_lbl = QLabel("Spotify Client ID:")
        lay_other.addWidget(self.spotify_id_lbl)
        self.inp_spotify_id = QLineEdit()
        lay_other.addWidget(self.inp_spotify_id)
        
        self.spotify_secret_lbl = QLabel("Spotify Client Secret:")
        lay_other.addWidget(self.spotify_secret_lbl)
        self.inp_spotify_secret = QLineEdit()
        self.inp_spotify_secret.setEchoMode(QLineEdit.EchoMode.Password)
        lay_other.addWidget(self.inp_spotify_secret)
        
        self.spotify_uri_lbl = QLabel("Spotify Redirect URI:")
        lay_other.addWidget(self.spotify_uri_lbl)
        self.inp_spotify_uri = QLineEdit()
        self.inp_spotify_uri.setText("http://127.0.0.1:8888/callback")
        lay_other.addWidget(self.inp_spotify_uri)
        
        spotify_auth_layout = QHBoxLayout()
        self.btn_spotify_login = QPushButton("Conectar con Spotify")
        self.lbl_spotify_status = QLabel("Consultando estado...")
        self.lbl_spotify_status.setStyleSheet("color: #a3a3a3; font-style: italic;")
        spotify_auth_layout.addWidget(self.btn_spotify_login)
        spotify_auth_layout.addWidget(self.lbl_spotify_status)
        lay_other.addLayout(spotify_auth_layout)
        
        self.btn_spotify_login.clicked.connect(self.connect_spotify)
        lay_other.addStretch()
        
        self.tabs.addTab(tab_api, "APIs & Core")
        self.tabs.addTab(tab_audio, "Audio & Voz")
        self.tabs.addTab(tab_other, "Spotify & Estilo")
        layout.addWidget(self.tabs)
        
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save Configurations")
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)
        
        self.btn_save.clicked.connect(self.save)
        self.load_settings()
        
    def load_settings(self):
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            
            self.cmb_mic.addItem("Default Microphone Input", "")
            for i, dev in enumerate(devices):
                if dev.get("max_input_channels", 0) > 0:
                    self.cmb_mic.addItem(dev["name"], i)
                    
            self.cmb_speaker.addItem("Default Speaker Output", "")
            for i, dev in enumerate(devices):
                if dev.get("max_output_channels", 0) > 0:
                    self.cmb_speaker.addItem(dev["name"], i)
        except Exception:
            pass
            
        try:
            from memory.config_manager import load_api_keys
            cfg = load_api_keys()
            
            self.inp_gemini.setText(cfg.get("gemini_api_key", ""))
            self.inp_openrouter.setText(cfg.get("openrouter_api_key", ""))
            self.chk_gpu.setChecked(cfg.get("gpu_acceleration", False))
            
            voice = cfg.get("jarvis_voice", "Aoede")
            for idx in range(self.cmb_voice.count()):
                if self.cmb_voice.itemData(idx) == voice:
                    self.cmb_voice.setCurrentIndex(idx)
                    break
                    
            theme = cfg.get("jarvis_theme", "gold")
            idx = self.cmb_theme.findData(theme)
            if idx >= 0:
                self.cmb_theme.setCurrentIndex(idx)
                
            llm = cfg.get("llm_model", "gemini-1.5-flash")
            idx = self.cmb_llm.findData(llm)
            if idx >= 0:
                self.cmb_llm.setCurrentIndex(idx)
                
            ai_prov = cfg.get("ai_provider", "gemini")
            idx = self.cmb_ai_provider.findData(ai_prov)
            if idx >= 0: self.cmb_ai_provider.setCurrentIndex(idx)
                
            mic = cfg.get("mic_device", "")
            idx = self.cmb_mic.findData(mic)
            if idx >= 0: self.cmb_mic.setCurrentIndex(idx)
            
            spk = cfg.get("speaker_device", "")
            idx = self.cmb_speaker.findData(spk)
            if idx >= 0: self.cmb_speaker.setCurrentIndex(idx)
            
            # Load Spotify configs
            self.inp_spotify_id.setText(cfg.get("spotify_client_id", ""))
            self.inp_spotify_secret.setText(cfg.get("spotify_client_secret", ""))
            self.inp_spotify_uri.setText(cfg.get("spotify_redirect_uri", "http://127.0.0.1:8888/callback"))
            
            # Check Spotify Auth status
            self.lbl_spotify_status.setText(self.check_spotify_auth_status())
            
        except Exception:
            pass
            
    def save(self):
        try:
            from memory.config_manager import save_api_keys
            theme_val = self.cmb_theme.currentData()
            
            cfg = {
                "gemini_api_key": self.inp_gemini.text().strip(),
                "openrouter_api_key": self.inp_openrouter.text().strip(),
                "jarvis_voice": self.cmb_voice.currentData(),
                "jarvis_theme": theme_val,
                "llm_model": self.cmb_llm.currentData(),
                "ai_provider": self.cmb_ai_provider.currentData(),
                "gpu_acceleration": self.chk_gpu.isChecked(),
                "mic_device": self.cmb_mic.currentData(),
                "speaker_device": self.cmb_speaker.currentData(),
                "spotify_client_id": self.inp_spotify_id.text().strip(),
                "spotify_client_secret": self.inp_spotify_secret.text().strip(),
                "spotify_redirect_uri": self.inp_spotify_uri.text().strip()
            }
            save_api_keys(cfg)
            
            apply_theme_tokens(theme_val)
            
            parent = self.parent()
            if parent:
                parent.update_theme_styles()
                
            QMessageBox.information(self, "Success", "JARVIS Configurations saved, sir.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    def check_spotify_auth_status(self):
        try:
            client_id = self.inp_spotify_id.text().strip()
            client_secret = self.inp_spotify_secret.text().strip()
            redirect_uri = self.inp_spotify_uri.text().strip()
            
            if not client_id or not client_secret:
                return "Falta configurar credenciales"
                
            import spotipy
            from spotipy.oauth2 import SpotifyOAuth
            sp_oauth = SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                open_browser=False
            )
            token = sp_oauth.get_cached_token()
            if token:
                return "✅ Conectado"
            else:
                return "⚠️ Desconectado"
        except Exception as e:
            return f"Error: {e}"

    def _manual_download_vosk(self):
        self.btn_download_vosk.setEnabled(False)
        self.btn_download_vosk.setText("Descargando en background...")
        import threading
        
        class Signaler(QObject):
            done = pyqtSignal(str)
            
        self._dl_signaler = Signaler()
        self._dl_signaler.done.connect(lambda text: self.btn_download_vosk.setText(text))
        
        def worker():
            try:
                import os
                model_path = "config/vosk_model"
                if os.path.exists(model_path):
                    import shutil
                    shutil.rmtree(model_path)
                import urllib.request
                import zipfile
                url = "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"
                zip_path = "vosk_model.zip"
                urllib.request.urlretrieve(url, zip_path)
                with zipfile.ZipFile(zip_path, 'r') as z:
                    z.extractall("config")
                extract_path = "config/vosk-model-small-es-0.42"
                os.rename(extract_path, model_path)
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                self._dl_signaler.done.emit("✅ Descargado (IA Local)")
            except Exception as e:
                self._dl_signaler.done.emit(f"❌ Error al descargar")
        threading.Thread(target=worker, daemon=True).start()

    def connect_spotify(self):
        client_id = self.inp_spotify_id.text().strip()
        client_secret = self.inp_spotify_secret.text().strip()
        redirect_uri = self.inp_spotify_uri.text().strip()
        
        if not client_id or not client_secret:
            QMessageBox.warning(self, "Spotify API", "Por favor, ingresa el Client ID y el Client Secret primero.")
            return
            
        # Temporarily save these settings so that the background OAuth flow can read them
        try:
            from memory.config_manager import load_api_keys, save_api_keys
            cfg = load_api_keys()
            cfg["spotify_client_id"] = client_id
            cfg["spotify_client_secret"] = client_secret
            cfg["spotify_redirect_uri"] = redirect_uri
            save_api_keys(cfg)
        except Exception:
            pass
            
        self.lbl_spotify_status.setText("⏳ Abriendo navegador...")
        self.btn_spotify_login.setEnabled(False)
        
        import threading
        def auth_worker():
            try:
                import spotipy
                from spotipy.oauth2 import SpotifyOAuth
                
                sp_oauth = SpotifyOAuth(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    scope="user-modify-playback-state user-read-playback-state user-read-currently-playing",
                    open_browser=True
                )
                
                # Triggers browser and starts spotipy's built-in local redirect listener
                token_info = sp_oauth.get_access_token(as_dict=False)
                if token_info:
                    QTimer.singleShot(0, self.spotify_auth_success)
                else:
                    QTimer.singleShot(0, lambda: self.spotify_auth_failed("No se obtuvo token."))
            except Exception as e:
                QTimer.singleShot(0, lambda: self.spotify_auth_failed(str(e)))
                
        threading.Thread(target=auth_worker, daemon=True).start()

    def spotify_auth_success(self):
        self.btn_spotify_login.setEnabled(True)
        self.lbl_spotify_status.setText("✅ Conectado")
        QMessageBox.information(self, "Spotify API", "¡Autenticación con Spotify exitosa, sir!")

    def spotify_auth_failed(self, error):
        self.btn_spotify_login.setEnabled(True)
        self.lbl_spotify_status.setText("❌ Error")
        QMessageBox.critical(self, "Spotify API Error", f"Fallo al conectar: {error}")

    def update_style(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {C_BG};
                border: 2px solid {C_PRI};
                border-radius: 10px;
            }}
            QLabel {{
                color: {C_TEXT};
                font-weight: bold;
            }}
            QLineEdit, QComboBox {{
                background: rgba(0,0,0,0.4);
                border: 1px solid {C_BORDER};
                color: white;
                padding: 5px;
                border-radius: 4px;
            }}
            QCheckBox {{
                color: {C_PRI};
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {C_PRI};
                color: black;
                font-weight: bold;
                padding: 6px 15px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: white;
            }}
            QTabWidget::pane {{
                border: 1px solid {C_BORDER};
                background: rgba(0, 0, 0, 0.2);
                border-radius: 6px;
            }}
            QTabBar::tab {{
                background: rgba(0, 0, 0, 0.4);
                color: {C_TEXT};
                padding: 8px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid {C_BORDER};
                border-bottom: none;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {C_PRI};
                color: black;
                font-weight: bold;
            }}
        """)


class MainWindow(QMainWindow):
    _shutdown_sig = pyqtSignal()

    def __init__(self, ui, face_path):
        super().__init__()
        self.ui = ui
        self.ui._win = self
        
        self.resize(1050, 760)
        self.setMinimumSize(1000, 750)
        
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        
        icon_path = (Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent) / "assets" / "jarvis_icono.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            
        self.header_container = QWidget(self.central_widget)
        header_bar = QHBoxLayout(self.header_container)
        header_bar.setContentsMargins(15, 8, 15, 8)
        
        self.lbl_brand = QLabel("J A R V I S")
        font = QFont("Century Gothic", 16, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 8.0)
        self.lbl_brand.setFont(font)
        header_bar.addWidget(self.lbl_brand)
        header_bar.addStretch()
        
        self.btn_settings = QPushButton()
        self.btn_play = QPushButton()
        self.btn_folder = QPushButton()
        self.btn_min = QPushButton()
        self.btn_close = QPushButton()
        
        self.head_buttons = [
            (self.btn_settings, 'fa5s.cog', self._open_settings),
            (self.btn_play, 'fa5s.play', self._toggle_mute),
            (self.btn_folder, 'fa5s.folder', self._open_folder),
            (self.btn_min, 'fa5s.window-minimize', self.showMinimized),
            (self.btn_close, 'fa5s.times', self.close)
        ]
        
        for btn, icon, cb in self.head_buttons:
            btn.setFixedSize(28, 28)
            btn.clicked.connect(cb)
            header_bar.addWidget(btn)
            
        self.orb = CustomParticleOrb(self.ui, self.central_widget)
        self.orb.lower()
        
        # Symmetrical Bento overlay dashboard container at bottom half
        self.bento_container = QWidget(self.central_widget)
        bento_layout = QGridLayout(self.bento_container)
        bento_layout.setContentsMargins(0, 0, 0, 0)
        bento_layout.setSpacing(15)
        
        # Aligned stretches
        bento_layout.setColumnStretch(0, 1)
        bento_layout.setColumnStretch(1, 1)
        bento_layout.setColumnStretch(2, 1)
        bento_layout.setColumnStretch(3, 1)
        
        self.spotify_w = SpotifyWidget()
        self.system_w = SystemWidget()
        self.todo_w = TodoWidget()
        self.notes_w = NotesWidget()
        self.files_panel = FilesPanel(self.ui)
        self.weather_w = WeatherWidget()
        
        # Highly Organized Symmetrical 2-row, 4-column layout at bottom half
        # Row 0
        bento_layout.addWidget(self.spotify_w, 0, 0, 1, 2)
        bento_layout.addWidget(self.weather_w, 0, 2, 1, 1)
        bento_layout.addWidget(self.system_w, 0, 3, 1, 1)
        
        # Row 1
        bento_layout.addWidget(self.todo_w, 1, 0, 1, 1)
        bento_layout.addWidget(self.notes_w, 1, 1, 1, 2)
        bento_layout.addWidget(self.files_panel, 1, 3, 1, 1)
        
        # Clean floating digital Clock Widget at top-right corner
        self.clock_w = ClockWidget(self.central_widget)
        
        # Dedicated Holographic Closed Captions Speech Area (Single centered line)
        self.txt_console = QLabel(self.central_widget)
        self.txt_console.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_console.setWordWrap(True)
        
        # Force Close flag and System Tray initialization
        self._force_close = False
        self.tray_icon = None
        self._setup_tray_icon()
        
        self.update_theme_styles()
        self._drag_pos = None
        self._shutdown_sig.connect(self._handle_shutdown)

    def update_theme_styles(self):
        self.central_widget.setStyleSheet(f"""
            QWidget#centralWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(28, 21, 6, 0.90), stop:1 rgba(10, 7, 2, 0.90));
                border: 2.2px solid {C_PRI};
                border-radius: 20px;
            }}
        """)
        self.lbl_brand.setStyleSheet(f"color: {C_PRI}; font-weight: bold; background: transparent;")
        
        for btn, icon, cb in self.head_buttons:
            if HAS_QTA:
                btn.setIcon(qta.icon(icon, color=C_PRI_DIM))
            btn.setStyleSheet(f"QPushButton {{ background: transparent; border: 1px solid rgba(120,53,15,0.35); border-radius: 14px; }} QPushButton:hover {{ background: rgba(245,158,11,0.1); border-color: {C_PRI}; }}")
            
        self.txt_console.setStyleSheet(f"QLabel {{ color: {C_PRI}; font-weight: bold; font-size: 15px; background: transparent; }}")
        
        self.spotify_w.update_style()
        self.system_w.update_style()
        self.todo_w.update_style()
        self.notes_w.update_style()
        self.files_panel.update_style()
        self.clock_w.update_style()
        self.weather_w.update_style()
        
        if hasattr(self, "orb"):
            self.orb.sync_theme()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        W = self.central_widget.width()
        H = self.central_widget.height()
        
        self.header_container.setGeometry(0, 0, W, 45)
        
        # Position digital Clock floating at top-right
        self.clock_w.setGeometry(W - 260, 50, 240, 70)
        
        # Position background Particle Orb Web capsule
        self.orb.setGeometry(0, 45, W, H - 45)
        
        # Position centered continuous speech line at bottom of HUD
        self.txt_console.setGeometry(30, H - 60, W - 60, 45)
        
        # Bento overlay container Y starts lower and ends exactly flush on top of the subtitles (gap-free!)
        bh = H // 3 + 30   # bottom-third height, lower widgets
        by = H - bh - 60   # positioned flush directly above speech subtitles
        self.bento_container.setGeometry(15, by, W - 30, bh)
        
        self.orb.lower()
        self.bento_container.raise_()
        self.txt_console.raise_()
        self.clock_w.raise_()

    def _open_settings(self):
        dialog = DeviceSettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if self.ui.on_config_saved:
                from memory.config_manager import load_api_keys
                self.ui.on_config_saved(load_api_keys())
            
    def _open_folder(self):
        try:
            from memory.config_manager import BASE_DIR
            os.startfile(BASE_DIR)
        except Exception:
            pass
            
    def _toggle_mute(self):
        self.ui.muted = not self.ui.muted
        self.orb.set_state("MUTED" if self.ui.muted else "LISTENING")
        if self.ui.muted:
            if self.ui.on_stop_command:
                self.ui.on_stop_command()

    def _setup_tray_icon(self):
        from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = (Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent) / "assets" / "jarvis_icono.ico"
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            from PyQt6.QtWidgets import QStyle
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
            
        tray_menu = QMenu(self)
        
        show_action = tray_menu.addAction("Mostrar JARVIS")
        show_action.triggered.connect(self.show_and_activate)
        
        mute_action = tray_menu.addAction("Silenciar/Escuchar")
        mute_action.triggered.connect(self._toggle_mute)
        
        tray_menu.addSeparator()
        
        exit_action = tray_menu.addAction("Salir")
        exit_action.triggered.connect(self._exit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def show_and_activate(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _exit_application(self):
        self._force_close = True
        self.close()
        import os
        os._exit(0)

    def _handle_shutdown(self):
        self._force_close = True
        self.close()

    def _on_tray_activated(self, reason):
        from PyQt6.QtWidgets import QSystemTrayIcon
        if reason in (QSystemTrayIcon.ActivationReason.DoubleClick, QSystemTrayIcon.ActivationReason.Trigger):
            if self.isVisible():
                self.hide()
            else:
                self.show_and_activate()

    def closeEvent(self, event):
        if getattr(self, "_force_close", False):
            event.accept()
        else:
            event.ignore()
            self.hide()
            if hasattr(self, "tray_icon") and self.tray_icon.isVisible():
                from PyQt6.QtWidgets import QSystemTrayIcon
                self.tray_icon.showMessage(
                    "JARVIS AI",
                    "Sigo activo en segundo plano. Presiona Insert para hablar o haz doble clic aquí para mostrarme.",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()


class MockRoot:
    def __init__(self, qapp: QApplication):
        self.qapp = qapp
        
    def mainloop(self):
        sys.exit(self.qapp.exec())
        
    def after(self, ms: int, func):
        QTimer.singleShot(ms, func)


class JarvisUI:
    def __init__(self, face_path=""):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.root = MockRoot(self.app)
        
        self.muted = False
        self.current_file = ""
        
        self.on_text_command = None
        self.on_stop_command = None
        self.on_config_saved = None
        
        self.jarvis_response_buffer = ""
        
        self._win = MainWindow(self, face_path)
        self._win.show()
        
        # Ensure startup shortcut is set up after 2 seconds (so it doesn't block startup)
        QTimer.singleShot(2000, self.ensure_startup_shortcut)
        
    def wait_for_api_key(self):
        pass

    def write_log(self, text: str):
        pass
        
    def set_state(self, state: str):
        self._win.orb.set_state(state)
        if state == "MUTED":
            self.muted = True
        elif state in ("LISTENING", "SPEAKING", "THINKING"):
            if self.muted:
                self.muted = False
                
    def set_audio_level(self, level: float):
        self._win.orb.set_audio(level)
        
    def clear_jarvis_response(self):
        self.jarvis_response_buffer = ""
        self._win.txt_console.setText("")
        
    def stream_jarvis_chunk(self, chunk: str):
        text = chunk.replace("JARVIS:", "").strip()
        if text:
            if self.jarvis_response_buffer:
                self.jarvis_response_buffer += " " + text
            else:
                self.jarvis_response_buffer = text
            self._win.txt_console.setText(self.jarvis_response_buffer)

    def ensure_startup_shortcut(self):
        try:
            import os
            import subprocess
            appdata = os.getenv('APPDATA')
            if not appdata:
                return
            startup_dir = os.path.join(appdata, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            shortcut_path = os.path.join(startup_dir, 'JARVIS AI.lnk')
            
            current_dir = str(Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent)
            
            if getattr(sys, 'frozen', False):
                target_exe = sys.executable
                icon_path = target_exe
            else:
                target_exe = os.path.join(current_dir, "Iniciar JARVIS Beta.vbs")
                icon_path = os.path.join(current_dir, "assets", "jarvis_icono.ico")
                if not os.path.exists(target_exe):
                    return
            
            ps_cmd = (
                f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{shortcut_path}');"
                f"$s.TargetPath='{target_exe}';"
                f"$s.WorkingDirectory='{current_dir}';"
                f"$s.IconLocation='{icon_path}';"
                f"$s.Description='Lanzador Automatico de JARVIS AI (Admin)';"
                f"$s.Save()"
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            print("[STARTUP] Startup shortcut ensured successfully.")
        except Exception as e:
            print(f"[STARTUP] Error ensuring startup shortcut: {e}")
