import sys, json
from spotapi import PublicPlaylist, PublicAlbum, Song

def check_pl():
    pl = PublicPlaylist("3XYcGNWAv85M5shLLyIMdD")
    for page in pl.paginate_playlist():
        items = page["items"]
        for item in items[:1]:
            track = item.get("itemV2", {}).get("data", {})
            print("Playlist track keys:", track.keys())
            if "albumOfTrack" in track:
                print("Album cover:", track["albumOfTrack"])
        break

check_pl()
