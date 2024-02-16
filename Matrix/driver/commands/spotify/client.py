from unidecode import unidecode
import spotipy
from spotipy.oauth2 import SpotifyOAuth


scope = [
        "user-read-playback-state",
        "user-library-read",
        "user-read-currently-playing",
    ]
    
client = None
def get_client():
    global client
    if client is None:
        auth_manager = SpotifyOAuth(scope=scope)
        client = spotipy.Spotify(auth_manager=auth_manager)
    return client


def parse_track_info(track):

    album = track["item"]["album"]
    album_name = album["name"]
    artist = album["artists"][0]
    artist_name = artist['name']
    images = album["images"]
    thumb=None
    for image in images:
        if thumb is None:
            thumb = image
        else:
            if thumb["width"] > image["width"]:
                thumb = image
    track_name = track["item"]["name"]
    track_duration = track["item"]["duration_ms"]
    track_id = track["item"]["id"]
    track_href = track["item"]["href"]
    track_position = track["progress_ms"]

    return {
        "track_name": unidecode(track_name),
        "track_id" : track_id,
        "track_duration" : track_duration,
        "track_href" : track_href,
        "track_position" : track_position,
        "album_name" : unidecode(album_name),
        "artist_name" : unidecode(artist_name),
        "thumbnail" : thumb["url"]
        }   

def get_current_track_info():
    cli = get_client()
    current_track = cli.current_playback()
    if current_track:
        return parse_track_info(current_track)
    return None

if __name__ == "__main__":

    print(get_current_track_info())
    