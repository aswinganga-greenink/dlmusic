import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, 
    QWidget, QPushButton, QLineEdit, QHBoxLayout, QGraphicsDropShadowEffect, QProgressBar
)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QCursor
import os

_STYLESHEET = """
QMainWindow {
    background-color: transparent;
}
QWidget#centralWidget {
    background-color: #0A0A0F;
    border-radius: 20px;
    border: 1px solid #1F1F2E;
}
QLabel#titleLabel {
    color: #FFFFFF;
    font-size: 48px;
    font-weight: 900;
    margin-top: 20px;
    letter-spacing: -2px;
}
QLabel#subtitleLabel {
    color: #8B8B9E;
    font-size: 15px;
    margin-bottom: 40px;
}
QLineEdit#urlInput {
    background-color: #13131A;
    border: 2px solid #272736;
    border-radius: 14px;
    color: #FFFFFF;
    padding: 18px 24px;
    font-size: 16px;
    selection-background-color: #4F46E5;
}
QLineEdit#urlInput:focus {
    border: 2px solid #4F46E5;
    background-color: #171721;
}
QPushButton#downloadBtn {
    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #4F46E5, stop:1 #7C3AED);
    color: #FFFFFF;
    border-radius: 14px;
    font-size: 18px;
    font-weight: bold;
    padding: 18px;
    margin-top: 20px;
}
QPushButton#downloadBtn:hover {
    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #6366F1, stop:1 #8B5CF6);
}
QPushButton#downloadBtn:pressed {
    background-color: #3730A3;
}
QPushButton#closeBtn {
    background-color: transparent;
    color: #8B8B9E;
    font-size: 16px;
    font-weight: bold;
    border: none;
}
QPushButton#closeBtn:hover {
    color: #EF4444;
}
QProgressBar {
    background-color: #13131A;
    border-radius: 6px;
    height: 12px;
    border: 1px solid #272736;
}
QProgressBar::chunk {
    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #4F46E5, stop:1 #8B5CF6);
    border-radius: 5px;
}
"""

class MockProgress:
    def add_task(self, *args, **kwargs): return 1
    def update(self, *args, **kwargs): pass
    def remove_task(self, *args, **kwargs): pass

class DownloaderThread(QThread):
    progress = pyqtSignal(int, int)
    log = pyqtSignal(str)
    finished_dl = pyqtSignal()

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.outdir = os.path.expanduser("~/Downloads/dlmusic")

    def run(self):
        try:
            from dlmusic.extractors import detect, collect
            from dlmusic.dedup import is_present
            from dlmusic.downloader import download_one
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            os.makedirs(self.outdir, exist_ok=True)
            self.log.emit("Detecting URL...")
            kind = detect(self.url)
            
            self.log.emit(f"Fetching metadata for {kind}...")
            items = collect(self.url, kind)
            
            to_download = []
            for item in items:
                if not is_present(item["query"], self.outdir):
                    to_download.append(item)
            
            total = len(to_download)
            if total == 0:
                self.log.emit("All tracks are already downloaded!")
                self.finished_dl.emit()
                return
                
            self.log.emit(f"Igniting Engine (4 Threads) for {total} tracks...")
            mock_prog = MockProgress()
            
            completed = 0
            with ThreadPoolExecutor(max_workers=4) as pool:
                futures = [
                    pool.submit(download_one, item, self.outdir, i+1, False, mock_prog, 1, "mp3")
                    for i, item in enumerate(to_download)
                ]
                for f in as_completed(futures):
                    success, title = f.result()
                    completed += 1
                    self.progress.emit(completed, total)
                    self.log.emit(f"Downloaded: {title[:40]}")
                    
            self.log.emit("All downloads complete! Check your Downloads folder.")
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
        # Frameless window and translucent background for perfect rounded corners
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(750, 450)
        
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        
        # Add drop shadow to give it that macOS/Windows 11 floating feel
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 10)
        self.central_widget.setGraphicsEffect(shadow)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Custom Title Bar
        self.title_bar = DraggableTitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        # Content Layout
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(80, 0, 80, 60)
        
        self.title_label = QLabel("dlmusic")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setObjectName("titleLabel")
        self.content_layout.addWidget(self.title_label)
        
        self.subtitle_label = QLabel("Paste a playlist URL below to begin mirroring.")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setObjectName("subtitleLabel")
        self.content_layout.addWidget(self.subtitle_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://open.spotify.com/playlist/...")
        self.url_input.setObjectName("urlInput")
        self.content_layout.addWidget(self.url_input)
        
        self.download_btn = QPushButton("Start Engine")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.download_btn.clicked.connect(self.start_download)
        self.content_layout.addWidget(self.download_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self.content_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #8B8B9E; margin-top: 10px; font-size: 13px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.status_label)
        
        self.content_layout.addStretch()
        self.main_layout.addLayout(self.content_layout)
        
        self.setStyleSheet(_STYLESHEET)

    def start_download(self):
        url = self.url_input.text().strip()
        if not url: return
        
        self.download_btn.setEnabled(False)
        self.download_btn.setText("Engine Running...")
        self.url_input.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.status_label.setText("Initializing backend...")
        
        self.worker = DownloaderThread(url)
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
        self.url_input.setEnabled(True)
        self.url_input.clear()

def run_gui():
    app = QApplication(sys.argv)
    
    # Attempt to load a modern sans-serif font like Inter if available, fallback to system sans-serif
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    window = DLMusicApp()
    window.show()
    sys.exit(app.exec())
