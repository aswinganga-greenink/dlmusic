import sys
import time
import shutil
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
    from rich.console import Console
    _console = Console()
except ImportError:
    print("Error: 'rich' library is required for my live UI.")
    print("Run: pip install rich --break-system-packages")
    sys.exit(1)

from dlmusic.config import state, banner, err, info, pr, step, DIM, R, BLU, CYN, MAG, BOLD, GRN, RED, YEL, WHT, ok
from dlmusic.extractors import detect, collect
from dlmusic.downloader import download_one

def main():
    """This is my primary entrypoint. It ties everything together."""
    parser = argparse.ArgumentParser(
        prog="dlmusic",
        description="Parallel Playlist → MP3 Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dlmusic playlist.txt ~/Music
  dlmusic "https://youtube.com/playlist?list=PLxxx" ~/Music --threads 6
  dlmusic "https://open.spotify.com/playlist/xxx" ~/Music --threads 4
        """
    )
    parser.add_argument("input",           help=".txt file or playlist URL")
    parser.add_argument("outdir",          nargs="?", default="./downloads", help="Output folder (default: ./downloads)")
    parser.add_argument("--threads", "-t", type=int, default=4,  help="Parallel download threads (default: 4)")
    parser.add_argument("--ejs",           action="store_true",   help="Enable remote EJS challenge solver (downloads from GitHub)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactively select tracks to skip")
    parser.add_argument("--format", "-f",  choices=["mp3", "flac", "m4a", "wav"], default="mp3", help="Audio format (default: mp3)")
    args = parser.parse_args()

    banner()

    # I always double-check my dependencies before starting so I don't fail halfway through.
    for dep in ("yt-dlp", "ffmpeg"):
        if not shutil.which(dep):
            err(f"Missing dependency: {dep}")
            sys.exit(1)

    kind   = detect(args.input)
    outdir = str(Path(args.outdir).expanduser())
    Path(outdir).mkdir(parents=True, exist_ok=True)

    info(f"Output folder : {CYN}{outdir}{R}")
    info(f"Threads       : {CYN}{args.threads}{R}")
    info(f"Input type    : {CYN}{kind}{R}")
    pr()

    items = collect(args.input, kind)
    if not items:
        err("No URLs or queries found in input.")
        sys.exit(1)

    # If I passed the interactive flag, I pause here and let the user prune the list
    if args.interactive:
        pr()
        pr(f"{BLU}{BOLD}  ➜  Interactive Track Selection{R}")
        for idx, item in enumerate(items, 1):
            pr(f"      {DIM}{idx:>3}.{R} {item}")
        pr()
        try:
            ans = input(f"{CYN}  ℹ  Enter track numbers to skip (e.g., 1, 4-7) or press Enter to download all: {R}").strip()
        except KeyboardInterrupt:
            pr()
            sys.exit(0)
            
        if ans:
            skip_indices = set()
            for part in ans.split(","):
                part = part.strip()
                if not part: continue
                if "-" in part:
                    try:
                        start, end = map(int, part.split("-"))
                        skip_indices.update(range(start, end + 1))
                    except ValueError:
                        pass
                else:
                    try:
                        skip_indices.add(int(part))
                    except ValueError:
                        pass
            items = [item for i, item in enumerate(items, 1) if i not in skip_indices]
            if not items:
                ok("All tracks skipped. Exiting.")
                sys.exit(0)

    state["total"] = len(items)
    info(f"Tracks to download  : {CYN}{state['total']}{R}")
    pr()
    step(f"Starting parallel download with {args.threads} threads…")
    pr()

    t_start = time.time()

    # I wrap everything in my rich UI Progress bar context to make it look professional
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=_console
    ) as progress:
        overall_task = progress.add_task("[bold magenta]Overall Progress", total=state["total"])

        results = [None] * len(items)
        
        # Here's where the magic happens. I throw all the queries into a thread pool
        # so yt-dlp can crush them concurrently. It's purely I/O bound so Python threads are perfect.
        with ThreadPoolExecutor(max_workers=args.threads) as pool:
            futures = {
                pool.submit(download_one, item, outdir, idx + 1, args.ejs, progress, overall_task, args.format): idx
                for idx, item in enumerate(items)
            }
            for f in as_completed(futures):
                idx = futures[f]
                success, title = f.result()
                if success:
                    results[idx] = title

    elapsed = time.time() - t_start

    # I thought generating an M3U file would be super handy for opening the folder in VLC right away
    m3u_file = Path(outdir) / f"{Path(outdir).name}.m3u"
    m3u_created = False
    if any(results):
        try:
            with open(m3u_file, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\\n")
                for title in results:
                    if title:
                        f.write(f"{title}.{args.format}\\n")
            m3u_created = True
        except Exception as e:
            warn(f"Could not generate M3U playlist: {e}")

    # Final summary display
    pr()
    pr(f"{MAG}{BOLD}  ╔═══════════════════════════════════════╗{R}")
    pr(f"{MAG}{BOLD}  ║           Download Summary            ║{R}")
    pr(f"{MAG}{BOLD}  ╚═══════════════════════════════════════╝{R}")
    pr(f"    {GRN}✔  Done    : {state['done']}{R}")
    pr(f"    {RED}✘  Failed  : {state['failed']}{R}")
    pr(f"    {CYN}⏱  Time    : {elapsed:.1f}s{R}")
    pr(f"    {WHT}📁  Saved to: {outdir}{R}")
    if m3u_created:
        pr(f"    {WHT}🎶  Playlist: {m3u_file.name}{R}")
    pr()

if __name__ == "__main__":
    main()
