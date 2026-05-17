<div align="center">
  <h1>🎵 dlmusic</h1>
  <p><b>An elite, highly concurrent playlist-to-audio engine for Linux.</b></p>
  
  [![CI Pipeline](https://github.com/aswinganga-greenink/dlmusic/actions/workflows/ci.yml/badge.svg)](https://github.com/aswinganga-greenink/dlmusic/actions/workflows/ci.yml)
  [![Release](https://img.shields.io/github/v/release/aswinganga-greenink/dlmusic)](https://github.com/aswinganga-greenink/dlmusic/releases)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

---

`dlmusic` is a professional-grade CLI tool built to flawlessly mirror massive Spotify, Apple Music, SoundCloud, and YouTube playlists to your local drive. It features an incredibly fast multi-threaded engine, automatic high-res metadata injection, and synced lyrics embedding.

## ✨ Elite Features

- 🏎️ **Extreme Concurrency**: Powered by a robust `ThreadPoolExecutor` architecture. Capable of downloading dozens of tracks simultaneously without breaking a sweat.
- 🎨 **Audiophile Metadata**: Bypasses YouTube's low-res thumbnails by scraping the public Spotify API for exact **640x640 High-Res Album Art** and injecting it natively.
- 🎤 **Auto-Scrolling Lyrics**: Integrates with LRCLIB to silently scrape and embed `.lrc` (Synchronized Lyrics) metadata into the ID3 tags of your MP3s. Play it on your phone and watch the lyrics auto-scroll!
- 🧠 **Smart Resume**: An intelligent `O(1)` manifest system guarantees you will never re-download an existing file if your connection drops. 
- 🖥️ **Awwwards-Level Native GUI**: Run `dlmusic` with zero arguments to trigger our brand new hardware-accelerated PyQt6 interface. Features cinematic glassmorphism, dynamic Light/Dark mode (`◑`), smooth slide animations, and full interactive track selection!
- 🎛️ **Total Granular Control**: Choose between MP3, FLAC, M4A, and WAV output formats, and crank your download concurrency up to 16 threads directly from the UI.

## 📦 Installation

**Method 1: Pipx (Recommended)**
```bash
pipx install git+https://github.com/aswinganga-greenink/dlmusic.git
```

**Method 2: Standalone Binary**
Go to the [Releases page](https://github.com/aswinganga-greenink/dlmusic/releases) and download the pre-compiled Linux binary. No Python required!

## 🚀 Usage

Download a Spotify playlist concurrently into `./downloads`:
```bash
dlmusic "https://open.spotify.com/playlist/3XYcGNWAv85M5shLLyIMdD"
```

Trigger the Interactive Wizard Mode:
```bash
dlmusic
```

Download a YouTube playlist using 8 threads into FLAC format, while interacting to skip tracks:
```bash
dlmusic "https://youtube.com/playlist?list=PLxxx" ~/Music -t 8 -f flac --interactive
```

## 🛠️ Architecture

* **Downloader**: `yt-dlp` (Core I/O)
* **Metadata Processing**: `mutagen` & `syncedlyrics` (Native ID3 manipulation)
* **Data Sources**: Spotify API (GraphQL), Apple Music, SoundCloud
* **UI Engine**: `rich` (Live Progress Bars & CLI Panels)

---
<div align="center">
  <i>Engineered with precision for the modern audiophile.</i>
</div>
