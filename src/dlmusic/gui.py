import sys, os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, 
    QWidget, QPushButton, QLineEdit, QHBoxLayout, QGraphicsDropShadowEffect, 
    QProgressBar, QComboBox, QSpinBox, QListWidget, QListWidgetItem, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QCursor

_STYLESHEET = """
QMainWindow { background-color: transparent; }
QWidget#centralWidget { background-color: #0A0A0F; border-radius: 20px; border: 1px solid #1F1F2E; }
QLabel#titleLabel { color: #FFFFFF; font-size: 36px; font-weight: 900; margin-top: 10px; letter-spacing: -2px; }
QLabel#subtitleLabel { color: #8B8B9E; font-size: 14px; margin-bottom: 20px; }
QLineEdit#urlInput { background-color: #13131A; border: 2px solid #272736; border-radius: 12px; color: #FFFFFF; padding: 12px 18px; font-size: 14px; selection-background-color: #4F46E5; }
QLineEdit#urlInput:focus { border: 2px solid #4F46E5; background-color: #171721; }
QPushButton#downloadBtn { background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #4F46E5, stop:1 #7C3AED); color: #FFFFFF; border-radius: 12px; font-size: 16px; font-weight: bold; padding: 14px; margin-top: 10px; }
QPushButton#downloadBtn:hover { background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #6366F1, stop:1 #8B5CF6); }
QPushButton#downloadBtn:disabled { background-color: #272736; color: #8B8B9E; }
QPushButton#fetchBtn, QPushButton#fileBtn { background-color: #1F1F2E; color: #FFFFFF; border-radius: 12px; padding: 12px; font-weight: bold; }
QPushButton#fetchBtn:hover, QPushButton#fileBtn:hover { background-color: #2D2D44; }
QPushButton#closeBtn { background-color: transparent; color: #8B8B9E; font-size: 16px; font-weight: bold; border: none; }
QPushButton#closeBtn:hover { color: #EF4444; }
QProgressBar { background-color: #13131A; border-radius: 6px; height: 10px; border: 1px solid #272736; }
QProgressBar::chunk { background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #4F46E5, stop:1 #8B5CF6); border-radius: 5px; }
QComboBox, QSpinBox { background-color: #13131A; border: 2px solid #272736; border-radius: 8px; color: #FFFFFF; padding: 8px; font-size: 13px; }
QListWidget { background-color: #13131A; border: 2px solid #272736; border-radius: 10px; color: #FFFFFF; padding: 5px; font-size: 13px; outline: 0; }
QListWidget::item { padding: 6px; border-bottom: 1px solid #1F1F2E; }
QListWidget::item:selected { background-color: #3730A3; border-radius: 5px; }
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
            
            os.makedirs(self.outdir, exist_ok=True)
            to_download = []
            
            self.log.emit("Scanning manifest for existing tracks...")
            for item in self.items:
                if not is_present(item["query"], self.outdir):
                    to_download.append(item)
            
            total = len(to_download)
            if total == 0:
                self.log.emit("All selected tracks are already downloaded!")
                self.finished_dl.emit()
                return
                
            self.log.emit(f"Igniting Engine ({self.threads} Threads) for {total} tracks...")
            mock_prog = MockProgress()
            
            completed = 0
            with ThreadPoolExecutor(max_workers=self.threads) as pool:
                futures = [
                    pool.submit(download_one, item, self.outdir, i+1, False, mock_prog, 1, self.audio_format)
                    for i, item in enumerate(to_download)
                ]
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
        self.layout.setContentsMargins(10, 10, 20, 0)
        self.layout.addStretch()
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_btn.clicked.connect(self.parent.close)
        self.layout.addWidget(self.close_btn)
        self.start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.parent.move(self.parent.pos() + delta)
            self.start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.start_pos = None

class DLMusicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(750, 650)
        
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 10)
        self.central_widget.setGraphicsEffect(shadow)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.main_layout.addWidget(DraggableTitleBar(self))
        
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(60, 0, 60, 40)
        
        self.title_label = QLabel("dlmusic")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setObjectName("titleLabel")
        self.content_layout.addWidget(self.title_label)
        
        self.subtitle_label = QLabel("The Ultimate Audiophile Engine.")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setObjectName("subtitleLabel")
        self.content_layout.addWidget(self.subtitle_label)
        
        # URL Input & File Picker Row
        self.url_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste Spotify, YouTube, or Apple Music link...")
        self.url_input.setObjectName("urlInput")
        self.url_row.addWidget(self.url_input)
        
        self.file_btn = QPushButton("📁")
        self.file_btn.setObjectName("fileBtn")
        self.file_btn.setFixedSize(45, 45)
        self.file_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.file_btn.clicked.connect(self.select_file)
        self.url_row.addWidget(self.file_btn)
        
        self.fetch_btn = QPushButton("Fetch")
        self.fetch_btn.setObjectName("fetchBtn")
        self.fetch_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.fetch_btn.clicked.connect(self.fetch_tracks)
        self.url_row.addWidget(self.fetch_btn)
        self.content_layout.addLayout(self.url_row)
        
        # Options Row (Format & Threads)
        self.options_row = QHBoxLayout()
        self.options_row.setContentsMargins(0, 10, 0, 10)
        
        self.format_label = QLabel("Format:")
        self.format_label.setStyleSheet("color: #8B8B9E; font-weight: bold;")
        self.options_row.addWidget(self.format_label)
        
        self.format_box = QComboBox()
        self.format_box.addItems(["mp3", "flac", "m4a", "wav"])
        self.options_row.addWidget(self.format_box)
        
        self.options_row.addSpacing(20)
        
        self.threads_label = QLabel("Threads:")
        self.threads_label.setStyleSheet("color: #8B8B9E; font-weight: bold;")
        self.options_row.addWidget(self.threads_label)
        
        self.threads_box = QSpinBox()
        self.threads_box.setRange(1, 16)
        self.threads_box.setValue(4)
        self.options_row.addWidget(self.threads_box)
        self.options_row.addStretch()
        self.content_layout.addLayout(self.options_row)
        
        # Track List (Interactive Selection)
        self.track_list = QListWidget()
        self.track_list.hide()
        self.content_layout.addWidget(self.track_list)
        
        self.download_btn = QPushButton("Start Engine")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(False) # Disabled until tracks are fetched
        self.content_layout.addWidget(self.download_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        self.content_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Awaiting input...")
        self.status_label.setStyleSheet("color: #8B8B9E; margin-top: 5px; font-size: 13px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.status_label)
        
        self.main_layout.addLayout(self.content_layout)
        self.setStyleSheet(_STYLESHEET)
        self.raw_items = []

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
            
        self.track_list.show()
        for item in items:
            list_item = QListWidgetItem(item.get("query", "Unknown Track"))
            list_item.setFlags(list_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            list_item.setCheckState(Qt.CheckState.Checked)
            self.track_list.addItem(list_item)
            
        self.download_btn.setEnabled(True)
        self.status_label.setText(f"Found {len(items)} tracks. Uncheck any you want to skip.")

    def start_download(self):
        selected_items = []
        for i in range(self.track_list.count()):
            if self.track_list.item(i).checkState() == Qt.CheckState.Checked:
                selected_items.append(self.raw_items[i])
                
        if not selected_items:
            self.status_label.setText("No tracks selected!")
            return
            
        self.download_btn.setEnabled(False)
        self.download_btn.setText("Engine Running...")
        self.fetch_btn.setEnabled(False)
        self.file_btn.setEnabled(False)
        self.url_input.setEnabled(False)
        self.track_list.setEnabled(False)
        
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        fmt = self.format_box.currentText()
        thrs = self.threads_box.value()
        
        self.worker = DownloaderThread(selected_items, fmt, thrs)
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.update_status)
        self.worker.finished_dl.connect(self.download_finished)
        self.worker.start()

    def update_progress(self, completed, total):
        pct = int((completed / total) * 100)
        self.progress_bar.setValue(pct)

    def update_status(self, msg):
        self.status_label.setText(msg)

    def download_finished(self):
        self.download_btn.setEnabled(True)
        self.download_btn.setText("Start Engine")
        self.fetch_btn.setEnabled(True)
        self.file_btn.setEnabled(True)
        self.url_input.setEnabled(True)
        self.track_list.setEnabled(True)

def run_gui():
    app = QApplication(sys.argv)
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    window = DLMusicApp()
    window.show()
    sys.exit(app.exec())
