import pytest
from dlmusic.dedup import _norm

def test_norm_strips_punctuation_and_lowercases():
    assert _norm("Hello, World!") == "hello world"
    assert _norm("Artist - Title (Official Audio)") == "artist title official audio"
    
def test_norm_handles_unicode():
    # Normalizes accented characters to standard ASCII for fuzzy matching
    assert _norm("Mukkuttippoo (feat. Jäyä)") == "mukkuttippoo feat jaya"
    assert _norm("Café") == "cafe"
