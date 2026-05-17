import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QLineEdit
from PyQt6.QtCore import Qt

class DLMusicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("dlmusic - Parallel Playlist Downloader")
        self.resize(800, 600)
        
        # Apply a dark, modern stylesheet later. For now, structural scaffolding.
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.title_label = QLabel("🎵 dlmusic v2.0.0 (Alpha)")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setObjectName("titleLabel")
        self.layout.addWidget(self.title_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Spotify or YouTube URL...")
        self.url_input.setObjectName("urlInput")
        self.layout.addWidget(self.url_input)
        
        self.download_btn = QPushButton("Start Download")
        self.download_btn.setObjectName("downloadBtn")
        self.layout.addWidget(self.download_btn)

def run_gui():
    app = QApplication(sys.argv)
    window = DLMusicApp()
    window.show()
    sys.exit(app.exec())
