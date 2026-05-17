import pytest
from dlmusic.extractors import detect

def test_detect_spotify():
    assert detect("https://open.spotify.com/playlist/3XYcGNWAv85M5shLLyIMdD") == "spotify"
    assert detect("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT") == "spotify"
    assert detect("http://open.spotify.com/album/something") == "spotify"

def test_detect_youtube_playlist():
    assert detect("https://www.youtube.com/playlist?list=PLxxx") == "yt_playlist"
    assert detect("https://music.youtube.com/playlist?list=PLxxx") == "yt_playlist"

def test_detect_youtube_single():
    assert detect("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "yt_single"
    assert detect("https://youtu.be/dQw4w9WgXcQ") == "yt_single"

def test_detect_txt_and_query():
    assert detect("never gonna give you up") == "query"
    assert detect("ytsearch1:never gonna give you up") == "query"
