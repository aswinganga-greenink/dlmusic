import threading

# I'm using ANSI escape codes here because I want the raw console output 
# to look gorgeous even if rich isn't invoked yet.
R = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[1;31m"
GRN = "\033[1;32m"
YEL = "\033[1;33m"
BLU = "\033[1;34m"
MAG = "\033[1;35m"
CYN = "\033[1;36m"
WHT = "\033[1;37m"

# Global lock so my threads don't step on each other's toes when updating counters
lock = threading.Lock()
state = {
    "done": 0,
    "failed": 0,
    "skipped": 0,
    "total": 0
}

def pr(msg="", **kw):
    with lock: print(msg, **kw)

def info(m):  pr(f"{CYN}  ℹ {R} {m}")
def ok(m):    pr(f"{GRN}  ✔ {R} {m}")
def warn(m):  pr(f"{YEL}  ⚠ {R} {m}")
def err(m):   pr(f"{RED}  ✘ {R} {m}")
def step(m):  pr(f"{BLU}{BOLD}  ➜ {R}{BOLD} {m}{R}")

def banner():
    pr(f"""
{MAG}{BOLD}  ╔═══════════════════════════════════════════════════╗
  ║  🎵  dlmusic — Parallel Playlist Downloader       ║
  ║      YouTube · YouTube Music · Spotify · TXT      ║
  ╚═══════════════════════════════════════════════════╝{R}
""")
