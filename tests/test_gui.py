import pytest
from PyQt6.QtCore import Qt
from dlmusic.gui import DLMusicApp

def test_gui_initialization(qtbot):
    """Production-grade assertion that our main window compiles and boots successfully."""
    window = DLMusicApp()
    qtbot.addWidget(window)
    
    assert window.windowTitle() == ""
    assert window.title_label.text() == "dlmusic"
    assert window.subtitle_label.text() == "Paste a playlist URL below to begin mirroring."
    
    # Assert default state of input fields
    assert window.url_input.placeholderText() == "https://open.spotify.com/playlist/..."
    
def test_gui_button_state(qtbot):
    """Assert interactive elements are wired up and accessible."""
    window = DLMusicApp()
    qtbot.addWidget(window)
    
    assert window.download_btn.text() == "Start Engine"
    assert window.download_btn.isEnabled()
