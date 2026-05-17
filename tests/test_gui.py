import pytest
from PyQt6.QtCore import Qt
from dlmusic.gui import DLMusicApp

def test_gui_initialization(qtbot):
    """Production-grade assertion that our main window compiles and boots successfully."""
    window = DLMusicApp()
    qtbot.addWidget(window)
    
    assert window.windowTitle() == "dlmusic - Parallel Playlist Downloader"
    assert window.title_label.text() == "🎵 dlmusic v2.0.0 (Alpha)"
    
    # Assert default state of input fields
    assert window.url_input.placeholderText() == "Enter Spotify or YouTube URL..."
    
def test_gui_button_state(qtbot):
    """Assert interactive elements are wired up and accessible."""
    window = DLMusicApp()
    qtbot.addWidget(window)
    
    assert window.download_btn.text() == "Start Download"
    assert window.download_btn.isEnabled()
