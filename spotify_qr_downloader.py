import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import qrcode
import json
from urllib.parse import urlencode

# Set up environment variables for Spotify authentication
os.environ["SPOTIPY_CLIENT_ID"] = ""
os.environ["SPOTIPY_CLIENT_SECRET"] = ""
os.environ["SPOTIPY_REDIRECT_URI"] = "http://127.0.0.1:8000/callback"


def setup_spotify():
    """Setup Spotify client with proper authentication"""
    auth_manager = SpotifyClientCredentials()
    return spotipy.Spotify(auth_manager=auth_manager)


def get_playlist_tracks(sp, playlist_id):
    """Get all tracks from a playlist"""
    results = sp.playlist_tracks(playlist_id)
    tracks = results["items"]
    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])
    return tracks


def create_track_files(track, base_filename):
    """Create QR code and metadata JSON for a track"""
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(track["external_urls"]["spotify"])
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f"{base_filename}.png")

    # Create metadata JSON
    metadata = {
        "name": track["name"],
        "artists": [artist["name"] for artist in track["artists"]],
        "release_year": track["album"]["release_date"][:4],
        "album": track["album"]["name"],
        "spotify_url": track["external_urls"]["spotify"],
    }

    with open(f"{base_filename}.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def main():
    # Create output directory
    if not os.path.exists("qr_codes"):
        os.makedirs("qr_codes")

    # Initialize Spotify client
    sp = setup_spotify()

    # Get the specific playlist
    playlists = sp.user_playlists("goupher")
    playlist_id = None

    for playlist in playlists["items"]:
        if playlist["name"] == "Schlickenriester 2":
            playlist_id = playlist["id"]
            break

    if playlist_id is None:
        print("Playlist 'Schlickenriester 2' not found!")
        return

    # Get tracks and create QR codes
    tracks = get_playlist_tracks(sp, playlist_id)
    print(f"\nGenerating QR codes for {len(tracks)} tracks...")

    for i, item in enumerate(tracks):
        track = item["track"]
        if track is None:
            continue

        track_name = track["name"]
        safe_name = "".join(
            x for x in track_name if x.isalnum() or x in (" ", "-", "_")
        )
        base_filename = f"qr_codes/{safe_name}"

        create_track_files(track, base_filename)
        print(f"Created QR code and metadata for: {track_name}")

    print("\nDone! QR codes have been saved in the 'qr_codes' directory.")


if __name__ == "__main__":
    main()
