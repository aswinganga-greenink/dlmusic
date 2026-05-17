import os
import subprocess
from typing import Tuple
from dlmusic.config import lock, state

import urllib.request

def embed_metadata(audio_path: str, cover_url: str, query: str):
    """Embeds high-res Spotify cover art and synced lyrics."""
    if not audio_path or not os.path.exists(audio_path):
        return
    try:
        import mutagen
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3, APIC, USLT
        from mutagen.flac import FLAC, Picture
        from mutagen.mp4 import MP4, MP4Cover
        
        # 1. Fetch Synced Lyrics
        import syncedlyrics
        lrc_text = syncedlyrics.search(query)
        
        # 2. Fetch Cover Art
        img_data = None
        if cover_url:
            req = urllib.request.Request(cover_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                img_data = resp.read()
            
        audio = mutagen.File(audio_path)
        if audio is None: return
            
        if isinstance(audio, MP3):
            if audio.tags is None: audio.add_tags()
            if img_data:
                audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=img_data))
            if lrc_text:
                audio.tags.add(USLT(encoding=3, lang='eng', desc='', text=lrc_text))
            audio.save()
        elif isinstance(audio, FLAC):
            if img_data:
                pic = Picture()
                pic.type, pic.mime, pic.desc, pic.data = 3, "image/jpeg", "Cover", img_data
                audio.add_picture(pic)
            if lrc_text:
                audio["LYRICS"] = lrc_text
            audio.save()
        elif isinstance(audio, MP4):
            if img_data:
                audio["covr"] = [MP4Cover(img_data, imageformat=MP4Cover.FORMAT_JPEG)]
            if lrc_text:
                audio["\xa9lyr"] = lrc_text
            audio.save()
    except Exception:
        pass  # Silently degrade if metadata embedding fails

def download_one(item: dict, outdir: str, idx: int, ejs: bool, progress, overall_task, audio_format: str) -> Tuple[bool, str]:
    """
    I wrote this to handle a single track download. It's designed to be completely 
    thread-safe so I can run 4 or 8 of these in parallel without the UI breaking.
    """
    url = item["query"]
    cover_url = item.get("cover", "")
    title = item.get("title", url[:55])
    search_url = f"ytsearch1:{url}" if not url.startswith("http") else url

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
        "--newline",
        "--no-warnings",
        "--concurrent-fragments", "4",
    ]
    
    # I sometimes hit the dreaded 'n-challenge' on YouTube, so I added an EJS solver toggle
    if ejs:
        cmd += ["--remote-components", "ejs:github"]
    cmd.append(search_url)

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        filepaths = []
        import re
        for line in iter(process.stdout.readline, ''):
            line = line.rstrip()
            if not line:
                continue
            if "[download]" in line and "%" in line:
                match = re.search(r"(\d+(?:\.\d+)?)%", line)
                if match:
                    progress.update(task_id, completed=float(match.group(1)), query=url)
            elif outdir in line:
                filepaths.append(line.strip())
                
        process.wait(timeout=600)
        if process.returncode == 0:
            with lock:
                state["done"] += 1
            progress.console.print(f"[green]✔[/green] [white]{title[:65]}[/white]")
            progress.remove_task(task_id)
            progress.advance(overall_task)
            
            # The filepath is printed to stdout by our --print after_move:filepath flag
            valid_paths = [p for p in filepaths if os.path.exists(p)]
            if valid_paths:
                embed_metadata(valid_paths[-1], cover_url, query=title)
            
            from dlmusic.dedup import record_done
            record_done(url, outdir)
            
            return True, title
        else:
            with lock:
                state["failed"] += 1
            progress.console.print(f"[red]✘[/red] {title[:50]} — download failed")
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
