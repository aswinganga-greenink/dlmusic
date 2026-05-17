import sys, os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, 
    QWidget, QPushButton, QLineEdit, QHBoxLayout, QGraphicsDropShadowEffect, 
    QProgressBar, QComboBox, QSpinBox, QListWidget, QListWidgetItem, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QCursor

def get_stylesheet(is_dark=True):
    if is_dark:
        bg = "transparent"
        central = "#050506"
        border = "rgba(255, 255, 255, 0.08)"
        card_bg = "rgba(255, 255, 255, 0.02)"
        text = "#F0F0F5"
        text_muted = "#8A8F98"
        input_bg = "#0A0A0C"
        input_focus = "#0F0F13"
        accent = "#5E6AD2"
        btn_hover = "#6F7AE0"
        btn_pressed = "#4651B5"
        selection_bg = "rgba(94, 106, 210, 0.15)"
        text_selection = "#3A3A4A"
    else:
        bg = "transparent"
        central = "#F7F7F9"
        border = "rgba(0, 0, 0, 0.08)"
        card_bg = "#FFFFFF"
        text = "#1A1A1F"
        text_muted = "#666677"
        input_bg = "#F0F0F4"
        input_focus = "#FFFFFF"
        accent = "#5E6AD2"
        btn_hover = "#6F7AE0"
        btn_pressed = "#4651B5"
        selection_bg = "rgba(94, 106, 210, 0.1)"
        text_selection = "#E0E0E5"
        
    return f"""
QMainWindow {{ background-color: {bg}; }}
QWidget#centralWidget {{ background-color: {central}; border-radius: 20px; border: 1px solid {border}; }}

/* Cards */
QWidget.Card {{ background-color: {card_bg}; border-radius: 14px; border: 1px solid {border}; }}

/* Typography */
QLabel#titleLabel {{ color: {text}; font-size: 42px; font-weight: 900; margin-top: 5px; letter-spacing: -2px; }}
QLabel#subtitleLabel {{ color: {text_muted}; font-size: 15px; margin-bottom: 15px; }}
QLabel {{ color: {text}; }}

/* Text Inputs */
QLineEdit#urlInput {{ background-color: {input_bg}; border: 1px solid {border}; border-radius: 10px; color: {text}; padding: 12px 18px; font-size: 14px; selection-background-color: {text_selection}; }}
QLineEdit#urlInput:focus {{ border: 1px solid {accent}; background-color: {input_focus}; }}

/* Buttons */
QPushButton#downloadBtn {{ background-color: {accent}; color: #FFFFFF; border-radius: 12px; font-size: 16px; font-weight: bold; padding: 14px; }}
QPushButton#downloadBtn:hover {{ background-color: {btn_hover}; }}
QPushButton#downloadBtn:pressed {{ background-color: {btn_pressed}; }}
QPushButton#downloadBtn:disabled {{ background-color: {card_bg}; color: {text_muted}; border: 1px solid {border}; }}

QPushButton#fetchBtn, QPushButton#fileBtn {{ background-color: {input_bg}; color: {text}; border: 1px solid {border}; border-radius: 10px; padding: 12px; font-weight: bold; font-size: 14px; }}
QPushButton#fetchBtn:hover, QPushButton#fileBtn:hover {{ background-color: {input_focus}; border: 1px solid {accent}; }}

QPushButton#closeBtn, QPushButton#themeBtn {{ background-color: transparent; color: {text_muted}; font-size: 18px; font-weight: bold; border: none; }}
QPushButton#closeBtn:hover {{ color: #EF4444; }}
QPushButton#themeBtn:hover {{ color: {accent}; }}

/* Progress Bar */
QProgressBar {{ background-color: {input_bg}; border-radius: 6px; height: 8px; border: none; margin-top: 10px; }}
QProgressBar::chunk {{ background-color: {accent}; border-radius: 4px; }}

/* Combo Box (Format Selection) */
QComboBox {{ background-color: {input_bg}; border: 1px solid {border}; border-radius: 8px; color: {text}; padding: 8px 12px; font-size: 14px; min-width: 70px; }}
QComboBox:hover {{ border: 1px solid {accent}; }}
QComboBox::drop-down {{ border: none; width: 30px; }}
QComboBox::down-arrow {{ image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid {text_muted}; margin-right: 10px; }}
QComboBox QAbstractItemView {{ background-color: {card_bg}; border: 1px solid {border}; border-radius: 8px; color: {text}; selection-background-color: {accent}; selection-color: #FFFFFF; outline: none; padding: 4px; }}

/* Spin Box (Threads Selection) */
QSpinBox {{ background-color: {input_bg}; border: 1px solid {border}; border-radius: 8px; color: {text}; padding: 8px 12px; font-size: 14px; min-width: 50px; }}
QSpinBox:hover {{ border: 1px solid {accent}; }}
QSpinBox::up-button, QSpinBox::down-button {{ background-color: transparent; border: none; width: 24px; }}
QSpinBox::up-arrow {{ border-left: 4px solid transparent; border-right: 4px solid transparent; border-bottom: 5px solid {text_muted}; }}
QSpinBox::down-arrow {{ border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid {text_muted}; }}
QSpinBox::up-button:hover QSpinBox::up-arrow {{ border-bottom-color: {accent}; }}
QSpinBox::down-button:hover QSpinBox::down-arrow {{ border-top-color: {accent}; }}

/* Interactive Track List */
QListWidget {{ background-color: {input_bg}; border: 1px solid {border}; border-radius: 12px; color: {text}; padding: 8px; font-size: 13px; outline: 0; }}
QListWidget::item {{ padding: 10px; border-bottom: 1px solid {border}; border-radius: 6px; }}
QListWidget::item:selected {{ background-color: {selection_bg}; border: 1px solid {accent}; color: {accent}; }}

/* Checkboxes inside List */
QListWidget::indicator {{ width: 18px; height: 18px; border: 2px solid {border}; border-radius: 4px; background-color: {card_bg}; }}
QListWidget::indicator:checked {{ background-color: {accent}; border: 2px solid {accent}; }}

/* Sleek Scrollbars */
QScrollBar:vertical {{ background-color: transparent; width: 8px; margin: 0px; }}
QScrollBar::handle:vertical {{ background-color: {border}; border-radius: 4px; min-height: 20px; }}
QScrollBar::handle:vertical:hover {{ background-color: {text_muted}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
"""

class MockProgress:
    def add_task(self, *args, **kwargs): return 1
    def update(self, *args, **kwargs): pass
    def remove_task(self, *args, **kwargs): pass

class FetcherThread(QThread):
    log = pyqtSignal(str)
    finished_fetch = pyqtSignal(list)
    def __init__(self, url):
        super().__init__()
        self.url = url
    def run(self):
        try:
            from dlmusic.extractors import detect, collect
            self.log.emit("Detecting link type...")
            kind = detect(self.url)
            self.log.emit(f"Scraping tracks ({kind})...")
            items = collect(self.url, kind)
            self.finished_fetch.emit(items)
        except Exception as e:
            self.log.emit(f"Error fetching: {e}")
            self.finished_fetch.emit([])

class DownloaderThread(QThread):
    progress = pyqtSignal(int, int)
    log = pyqtSignal(str)
    finished_dl = pyqtSignal()
    def __init__(self, items, audio_format, threads):
        super().__init__()
        self.items = items
        self.audio_format = audio_format
        self.threads = threads
        self.outdir = os.path.expanduser("~/Downloads/dlmusic")
    def run(self):
        try:
            from dlmusic.dedup import is_present
            from dlmusic.downloader import download_one
            from concurrent.futures import ThreadPoolExecutor, as_completed
            import os
            os.makedirs(self.outdir, exist_ok=True)
            to_download = [item for item in self.items if not is_present(item["query"], self.outdir)]
            
            total = len(to_download)
            if total == 0:
                self.log.emit("All selected tracks are already downloaded!")
                self.finished_dl.emit()
                return
                
            self.log.emit(f"Igniting Engine ({self.threads} Threads) for {total} tracks...")
            mock_prog = MockProgress()
            completed = 0
            with ThreadPoolExecutor(max_workers=self.threads) as pool:
                futures = [pool.submit(download_one, item, self.outdir, i+1, False, mock_prog, 1, self.audio_format) for i, item in enumerate(to_download)]
                for f in as_completed(futures):
                    success, title = f.result()
                    completed += 1
                    self.progress.emit(completed, total)
                    self.log.emit(f"Downloaded: {title[:40]}")
                    
            self.log.emit("All downloads complete! Check ~/Downloads/dlmusic")
            self.finished_dl.emit()
        except Exception as e:
            self.log.emit(f"Error: {e}")
            self.finished_dl.emit()

class DraggableTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 20, 0)
        self.layout.addStretch()
        
        self.theme_btn = QPushButton("◑")
        self.theme_btn.setObjectName("themeBtn")
        self.theme_btn.setFixedSize(30, 30)
        self.theme_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.theme_btn.clicked.connect(self.parent.toggle_theme)
        self.layout.addWidget(self.theme_btn)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_btn.clicked.connect(self.parent.close)
        self.layout.addWidget(self.close_btn)
        
        self.start_pos = None
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.start_pos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.parent.move(self.parent.pos() + delta)
            self.start_pos = event.globalPosition().toPoint()
    def mouseReleaseEvent(self, event):
        self.start_pos = None

class CardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setProperty("class", "Card")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

class DLMusicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_dark = True
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(780, 720)
        
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(50)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.shadow.setOffset(0, 15)
        self.central_widget.setGraphicsEffect(self.shadow)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.main_layout.addWidget(DraggableTitleBar(self))
        
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(50, 0, 50, 40)
        self.content_layout.setSpacing(15)
        
        self.title_label = QLabel("dlmusic")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setObjectName("titleLabel")
        self.content_layout.addWidget(self.title_label)
        
        self.subtitle_label = QLabel("The Ultimate Audiophile Engine.")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setObjectName("subtitleLabel")
        self.content_layout.addWidget(self.subtitle_label)
        
        # --- Card 1: Input Source ---
        self.card_input = CardWidget()
        self.url_row = QHBoxLayout()
        self.url_row.setSpacing(10)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste Spotify, YouTube, or Apple Music link...")
        self.url_input.setObjectName("urlInput")
        self.url_row.addWidget(self.url_input)
        
        self.file_btn = QPushButton("📁")
        self.file_btn.setObjectName("fileBtn")
        self.file_btn.setFixedSize(46, 46)
        self.file_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.file_btn.clicked.connect(self.select_file)
        self.url_row.addWidget(self.file_btn)
        
        self.fetch_btn = QPushButton("Fetch")
        self.fetch_btn.setObjectName("fetchBtn")
        self.fetch_btn.setFixedSize(80, 46)
        self.fetch_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.fetch_btn.clicked.connect(self.fetch_tracks)
        self.url_row.addWidget(self.fetch_btn)
        self.card_input.layout.addLayout(self.url_row)
        self.content_layout.addWidget(self.card_input)
        
        # --- Card 2: Configuration ---
        self.card_config = CardWidget()
        self.options_row = QHBoxLayout()
        self.options_row.setContentsMargins(5, 5, 5, 5)
        
        self.format_label = QLabel("Codec:")
        self.format_label.setStyleSheet("font-weight: bold; color: #8A8F98;")
        self.options_row.addWidget(self.format_label)
        self.format_box = QComboBox()
        self.format_box.addItems(["mp3", "flac", "m4a", "wav"])
        self.options_row.addWidget(self.format_box)
        
        self.options_row.addSpacing(40)
        
        self.threads_label = QLabel("Concurrency:")
        self.threads_label.setStyleSheet("font-weight: bold; color: #8A8F98;")
        self.options_row.addWidget(self.threads_label)
        self.threads_box = QSpinBox()
        self.threads_box.setRange(1, 16)
        self.threads_box.setValue(4)
        self.options_row.addWidget(self.threads_box)
        
        self.options_row.addStretch()
        self.card_config.layout.addLayout(self.options_row)
        self.content_layout.addWidget(self.card_config)
        
        # --- Track List (Hidden until fetched) ---
        self.track_list = QListWidget()
        self.track_list.setMaximumHeight(0) # For smooth expansion animation
        self.content_layout.addWidget(self.track_list)
        
        # --- Action Row ---
        self.download_btn = QPushButton("Start Engine")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(False)
        self.content_layout.addWidget(self.download_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(0)
        self.content_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Awaiting input...")
        self.status_label.setStyleSheet("color: #8B8B9E; margin-top: 5px; font-size: 13px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.status_label)
        
        self.content_layout.addStretch()
        self.main_layout.addLayout(self.content_layout)
        self.apply_theme()
        self.raw_items = []
        
        # --- Global Fade-in Animation ---
        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(800)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.fade_anim.start()

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.apply_theme()
        
    def apply_theme(self):
        self.setStyleSheet(get_stylesheet(self.is_dark))
        if self.is_dark: self.shadow.setColor(QColor(0, 0, 0, 160))
        else:            self.shadow.setColor(QColor(0, 0, 0, 50))

    def select_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select text file", "", "Text Files (*.txt)")
        if filename:
            self.url_input.setText(filename)
            self.fetch_tracks()

    def fetch_tracks(self):
        url = self.url_input.text().strip()
        if not url: return
        self.fetch_btn.setEnabled(False)
        self.status_label.setText("Fetching metadata...")
        
        self.fetcher = FetcherThread(url)
        self.fetcher.log.connect(self.update_status)
        self.fetcher.finished_fetch.connect(self.populate_list)
        self.fetcher.start()

    def populate_list(self, items):
        self.raw_items = items
        self.fetch_btn.setEnabled(True)
        self.track_list.clear()
        if not items:
            self.status_label.setText("No tracks found.")
            return
            
        for item in items:
            list_item = QListWidgetItem(item.get("query", "Unknown Track"))
            list_item.setFlags(list_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            list_item.setCheckState(Qt.CheckState.Checked)
            self.track_list.addItem(list_item)
            
        # Smoothly expand the list widget!
        self.anim_list = QPropertyAnimation(self.track_list, b"maximumHeight")
        self.anim_list.setDuration(600)
        self.anim_list.setStartValue(0)
        self.anim_list.setEndValue(250)
        self.anim_list.setEasingCurve(QEasingCurve.Type.OutExpo)
        self.anim_list.start()
        
        self.download_btn.setEnabled(True)
        self.status_label.setText(f"Found {len(items)} tracks. Uncheck any you want to skip.")

    def start_download(self):
        selected_items = [self.raw_items[i] for i in range(self.track_list.count()) if self.track_list.item(i).checkState() == Qt.CheckState.Checked]
        if not selected_items:
            self.status_label.setText("No tracks selected!")
            return
            
        self.download_btn.setEnabled(False)
        self.download_btn.setText("Engine Running...")
        self.fetch_btn.setEnabled(False)
        self.file_btn.setEnabled(False)
        self.url_input.setEnabled(False)
        
        # Smoothly expand progress bar
        self.progress_bar.setValue(0)
        self.anim_prog = QPropertyAnimation(self.progress_bar, b"maximumHeight")
        self.anim_prog.setDuration(400)
        self.anim_prog.setStartValue(0)
        self.anim_prog.setEndValue(8)
        self.anim_prog.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim_prog.start()
        
        self.worker = DownloaderThread(selected_items, self.format_box.currentText(), self.threads_box.value())
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.update_status)
        self.worker.finished_dl.connect(self.download_finished)
        self.worker.start()

    def update_progress(self, completed, total):
        self.progress_bar.setValue(int((completed / total) * 100))

    def update_status(self, msg):
        self.status_label.setText(msg)

    def download_finished(self):
        self.download_btn.setEnabled(True)
        self.download_btn.setText("Start Engine")
        self.fetch_btn.setEnabled(True)
        self.file_btn.setEnabled(True)
        self.url_input.setEnabled(True)
        
        # Collapse progress bar gracefully
        self.anim_prog = QPropertyAnimation(self.progress_bar, b"maximumHeight")
        self.anim_prog.setDuration(800)
        self.anim_prog.setStartValue(8)
        self.anim_prog.setEndValue(0)
        self.anim_prog.setEasingCurve(QEasingCurve.Type.InExpo)
        self.anim_prog.start()

def run_gui():
    app = QApplication(sys.argv)
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    window = DLMusicApp()
    window.show()
    sys.exit(app.exec())
