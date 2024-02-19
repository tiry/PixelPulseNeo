from unidecode import unidecode
from typing import Any
import spotipy
from spotipy.oauth2 import SpotifyOAuth


scope: list[str] = [
    "user-read-playback-state",
    "user-library-read",
    "user-read-currently-playing",
]

client = None


def get_client() -> spotipy.Spotify:
    global client
    if client is None:
        auth_manager = SpotifyOAuth(scope=scope)
        client = spotipy.Spotify(auth_manager=auth_manager)
    return client


def parse_track_info(track: dict[str, Any]) -> dict[str, Any]:
    album: dict = track["item"]["album"]
    album_name: str = album["name"]
    artist: dict = album["artists"][0]
    artist_name: str = artist["name"]
    images: list[dict] = album["images"]
    thumb: dict | None = None
    for image in images:
        if thumb is None:
            thumb = image
        else:
            if thumb["width"] > image["width"]:
                thumb = image
    track_name: str = track["item"]["name"]
    track_duration: int = track["item"]["duration_ms"]
    track_id: str = track["item"]["id"]
    track_href: str = track["item"]["href"]
    track_position: int = track["progress_ms"]

    thumb_url: str | None = None
    if thumb:
        thumb_url = thumb["url"]

    return {
        "track_name": unidecode(track_name),
        "track_id": track_id,
        "track_duration": track_duration,
        "track_href": track_href,
        "track_position": track_position,
        "album_name": unidecode(album_name),
        "artist_name": unidecode(artist_name),
        "thumbnail": thumb_url,
    }


def get_current_track_info() -> dict[str, Any] | None:
    cli: spotipy.Spotify = get_client()
    current_track: Any | None = cli.current_playback()
    if current_track:
        return parse_track_info(current_track)
    return None


if __name__ == "__main__":
    print(get_current_track_info())
