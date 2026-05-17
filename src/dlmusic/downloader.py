import os
import subprocess
from typing import Tuple
from dlmusic.config import lock, state

def download_one(url: str, outdir: str, idx: int, ejs: bool, progress, overall_task, audio_format: str) -> Tuple[bool, str]:
    """
    I wrote this to handle a single track download. It's designed to be completely 
    thread-safe so I can run 4 or 8 of these in parallel without the UI breaking.
    """
    # If I get a plain search string (like from Spotify), I prepend 'ytsearch1:' for yt-dlp
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
        "--quiet",
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
