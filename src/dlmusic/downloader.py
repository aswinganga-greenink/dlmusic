import os
import subprocess
from typing import Tuple
from dlmusic.config import lock, state

import urllib.request

def embed_cover_art(audio_path: str, cover_url: str):
    """I built this to strictly embed high-res Spotify cover art if it's available, replacing the yt-dlp thumbnail."""
    if not cover_url or not audio_path or not os.path.exists(audio_path):
        return
    try:
        import mutagen
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3, APIC
        from mutagen.flac import FLAC, Picture
        from mutagen.mp4 import MP4, MP4Cover
        
        req = urllib.request.Request(cover_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            img_data = resp.read()
            
        audio = mutagen.File(audio_path)
        if audio is None: return
            
        if isinstance(audio, MP3):
            if audio.tags is None: audio.add_tags()
            audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=img_data))
            audio.save()
        elif isinstance(audio, FLAC):
            pic = Picture()
            pic.type, pic.mime, pic.desc, pic.data = 3, "image/jpeg", "Cover", img_data
            audio.add_picture(pic)
            audio.save()
        elif isinstance(audio, MP4):
            audio["covr"] = [MP4Cover(img_data, imageformat=MP4Cover.FORMAT_JPEG)]
            audio.save()
    except Exception:
        pass  # If it fails, we gracefully fall back to whatever yt-dlp embedded

def download_one(item: dict, outdir: str, idx: int, ejs: bool, progress, overall_task, audio_format: str) -> Tuple[bool, str]:
    """
    I wrote this to handle a single track download. It's designed to be completely 
    thread-safe so I can run 4 or 8 of these in parallel without the UI breaking.
    """
    url = item["query"]
    cover_url = item.get("cover", "")
    search_url = f"ytsearch1:{url}" if not url.startswith("http") else url
    label = url[:55]

    # I do a quick, silent pre-flight check to fetch the actual video title for the UI
    try:
        raw = subprocess.check_output(
            ["yt-dlp", "--no-playlist", "--get-title", "--js-runtimes", "node",
             "--quiet", search_url],
            stderr=subprocess.DEVNULL, timeout=30, text=True
        ).strip()
        title = raw.splitlines()[0] if raw else label
    except Exception:
        title = label

    # Add a spinner to my rich UI so the user knows this specific thread is working
    task_id = progress.add_task(f"[cyan]{title[:45]}...", start=True, total=None)

    cmd = [
        "yt-dlp", "--no-playlist",
        "--extract-audio", "--audio-format", audio_format, "--audio-quality", "0",
        "--embed-thumbnail", "--embed-metadata", "--add-metadata",
        "--js-runtimes", "node",
        "--format", "bestaudio/best",
        "--output", os.path.join(outdir, "%(title)s.%(ext)s"),
        "--print", "after_move:filepath",
        "--quiet",
        "--no-warnings"
    ]
    
    # I sometimes hit the dreaded 'n-challenge' on YouTube, so I added an EJS solver toggle
    if ejs:
        cmd += ["--remote-components", "ejs:github"]
    cmd.append(search_url)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            with lock:
                state["done"] += 1
            progress.console.print(f"[green]✔[/green] [white]{title[:65]}[/white]")
            progress.remove_task(task_id)
            progress.advance(overall_task)
            
            # The filepath is printed to stdout by our --print after_move:filepath flag
            filepaths = [line for line in result.stdout.strip().splitlines() if os.path.exists(line)]
            if filepaths and cover_url:
                embed_cover_art(filepaths[-1], cover_url)
            
            from dlmusic.dedup import record_done
            record_done(url, outdir)
            
            return True, title
        else:
            emsg = result.stderr.strip().splitlines()[-1][:80] if result.stderr.strip() else "unknown error"
            with lock:
                state["failed"] += 1
            progress.console.print(f"[red]✘[/red] {title[:50]} — [dim]{emsg}[/dim]")
            progress.remove_task(task_id)
            progress.advance(overall_task)
            return False, title
    except subprocess.TimeoutExpired:
        with lock:
            state["failed"] += 1
        progress.console.print(f"[red]✘[/red] {title[:50]} — timed out")
        progress.remove_task(task_id)
        progress.advance(overall_task)
        return False, title
    except Exception as ex:
        with lock:
            state["failed"] += 1
        progress.console.print(f"[red]✘[/red] {title[:50]} — {str(ex)[:60]}")
        progress.remove_task(task_id)
        progress.advance(overall_task)
        return False, title
