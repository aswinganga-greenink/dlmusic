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
    I wrote this two-phase check:
    1. O(1) manifest lookup for blazing fast resumes on tracks we know we downloaded.
    2. Fallback to O(N) fuzzy filename overlap (>= 65%) to catch older files.
    """
    manifest = Path(outdir) / _MANIFEST
    if manifest.exists():
        if query in set(manifest.read_text(encoding="utf-8").splitlines()):
            return True

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
    """Thread-safe append to the manifest so future runs skip this track instantly."""
    manifest = Path(outdir) / _MANIFEST
    with lock:
        with open(manifest, "a", encoding="utf-8") as fh:
            fh.write(query + "\n")
