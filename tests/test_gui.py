import pytest
from PyQt6.QtCore import Qt
from dlmusic.gui import DLMusicApp

def test_gui_initialization(qtbot):
    """Production-grade assertion that our main window compiles and boots successfully."""
    window = DLMusicApp()
    qtbot.addWidget(window)
    
    assert window.windowTitle() == ""
    assert window.title_label.text() == "dlmusic"
    assert window.subtitle_label.text() == "The Ultimate Audiophile Engine."
    
    # Assert default state of input fields
    assert window.url_input.placeholderText() == "Paste Spotify, YouTube, or Apple Music link..."
    
def test_gui_button_state(qtbot):
    """Assert interactive elements are wired up and accessible."""
    window = DLMusicApp()
    qtbot.addWidget(window)
    
    assert window.download_btn.text() == "Start Engine"
    assert not window.download_btn.isEnabled() # Should be disabled until tracks are fetched
    
    assert window.format_box.currentText() == "mp3"
    assert window.threads_box.value() == 4
    
    assert window.fetch_btn.text() == "Fetch"
