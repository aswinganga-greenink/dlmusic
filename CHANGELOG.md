# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2026-05-17
### Added
- **Smart Resume (Pre-Scan)**: Instantly skip existing tracks in the output folder using a combination of O(1) `.dlmusic_manifest` lookups and robust O(N) fuzzy-filename checking.

## [1.0.0] - 2026-05-17
### Added
- Complete rewrite into a modular Python package structure.
- **Extractors**: Native extraction for Spotify playlists/albums via `spotapi` (bypassing the 25-track limit).
- **Core Engine**: ThreadPoolExecutor architecture for incredibly fast, parallel I/O.
- **UI System**: Live terminal progress UI built with `rich`.
- **Interactive Mode**: `-i` flag (or zero-argument CLI wizard) to selectively prune tracks before downloading.
- **M3U Generator**: Automatically builds `.m3u` playlist files in the output directory preserving original order.
- **Formats**: Support for `--format {mp3,flac,m4a,wav}`.
