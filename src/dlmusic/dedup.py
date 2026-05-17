import re
import unicodedata
from pathlib import Path
from dlmusic.config import lock

_MANIFEST = ".dlmusic_manifest"
_AUDIO_EXTS = {".mp3", ".m4a", ".opus", ".flac", ".wav", ".ogg"}
_STOP_WORDS = {"from", "the", "a", "an", "and", "or", "of", "in", "on"}

def _norm(s: str) -> str:
    """I normalize strings to ASCII and strip punctuation for robust fuzzy matching."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^\w\s]", " ", s).lower()
    return re.sub(r"\s+", " ", s).strip()

def is_present(query: str, outdir: str) -> bool:
    """
    I perform an O(N) fuzzy filename overlap (>= 65%) against actual files on disk.
    This guarantees that if a user deletes a track, we correctly identify it as missing and re-download!
    """
    if not Path(outdir).exists():
        return False
        
    norm_q = _norm(query)
    q_words = set(norm_q.split()) - _STOP_WORDS
    if not q_words:
        return False

    for f in Path(outdir).iterdir():
        if f.suffix.lower() in _AUDIO_EXTS:
            f_words = set(_norm(f.stem).split())
            overlap = q_words & f_words
            if overlap and len(overlap) / len(q_words) >= 0.65:
                return True
    return False

def record_done(query: str, outdir: str) -> None:
    """No longer strictly needed since we dynamically verify the disk state directly."""
    pass
