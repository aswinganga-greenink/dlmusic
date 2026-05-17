import re
import sys
import subprocess
from pathlib import Path
from typing import List
from dlmusic.config import err, step, warn

# I pre-compile my regex patterns here so they run as fast as possible during detection
_re_spotify = re.compile(r"https?://open\.spotify\.com/(playlist|album|track)/[\w]+")
_re_yt_list = re.compile(r"(youtube\.com|music\.youtube\.com).*(list=|/playlist)")
_re_yt      = re.compile(r"https?://(www\.)?(youtube\.com|youtu\.be|music\.youtube\.com)")

def detect(inp: str) -> str:
    """I built this to auto-detect what kind of link or file the user gave me."""
    if Path(inp).is_file() and inp.endswith(".txt"): return "txt"
    if _re_spotify.search(inp):  return "spotify"
    if _re_yt_list.search(inp):  return "yt_playlist"
    if _re_yt.search(inp):       return "yt_single"
    return "query"

def spotify_to_queries(url: str) -> List[str]:
    """
    I use the spotapi library here because it lets me fetch public Spotify data 
    without needing OAuth credentials. Super convenient.
    """
    try:
        from spotapi import PublicPlaylist, PublicAlbum, Song
    except ImportError as e:
        err(f"spotapi import failed: {e}")
        err("Run: pip install spotapi --break-system-packages")
        sys.exit(1)

    match = re.search(r"spotify\.com/(playlist|album|track)/([A-Za-z0-9]+)", url)
    if not match:
        err(f"Cannot parse Spotify URL: {url}")
        return []

    kind, item_id = match.group(1), match.group(2)
    step(f"Fetching Spotify {kind} metadata…")

    try:
        if kind == "playlist":
            pl      = PublicPlaylist(item_id)
            queries = []
            # I fixed a bug here previously! paginate_playlist is a generator
            # that seamlessly fetches all pages, bypassing the 25-track limit.
            for page in pl.paginate_playlist():
                items = page["items"]
                for item in items:
                    track   = item.get("itemV2", {}).get("data", {})
                    name    = track.get("name", "")
                    artists = track.get("artists", {}).get("items", [])
                    artist  = artists[0]["profile"]["name"] if artists else ""
                    if name:
                        queries.append(f"{artist} - {name}" if artist else name)
            return queries

        elif kind == "album":
            data  = PublicAlbum(item_id).get_album_info()
            items = data["data"]["albumUnion"]["tracks"]["items"]
            queries = []
            for item in items:
                track   = item.get("track", {})
                name    = track.get("name", "")
                artists = track.get("artists", {}).get("items", [])
                artist  = artists[0]["profile"]["name"] if artists else ""
                if name:
                    queries.append(f"{artist} - {name}" if artist else name)
            return queries

        elif kind == "track":
            data    = Song(item_id).get_track_info()
            name    = data.get("name", "")
            artists = data.get("artists", {}).get("items", [])
            artist  = artists[0]["profile"]["name"] if artists else ""
            return [f"{artist} - {name}" if artist else name]

    except Exception as e:
        err(f"Spotify fetch failed: {type(e).__name__}: {e}")
        return []

    return []

def collect(inp: str, kind: str) -> List[str]:
    """I gather all the URLs or search queries before I hand them to the threads."""
    if kind == "txt":
        lines = Path(inp).read_text().splitlines()
        return [l.strip() for l in lines if l.strip() and not l.startswith("#")]

    if kind == "spotify":
        return spotify_to_queries(inp)

    if kind in ("yt_playlist", "yt_single"):
        step("Fetching playlist entries from YouTube…")
        try:
            # I rely on yt-dlp's flat-playlist here so it's blazingly fast
            out = subprocess.check_output(
                ["yt-dlp", "--flat-playlist", "--get-url", "--quiet", inp],
                stderr=subprocess.DEVNULL, timeout=90, text=True
            )
            urls = [u.strip() for u in out.splitlines() if u.strip()]
            return urls if urls else [inp]
        except Exception as e:
            warn(f"Playlist extract failed ({e}), treating as single URL.")
            return [inp]

    return [inp]  # I default to returning it as a single URL or bare query string
