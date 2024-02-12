import spotipy
from spotipy.oauth2 import SpotifyOAuth


if __name__ == "__main__":
    birdy_uri = "spotify:artist:2WX2uTcsvV5OnS0inACecP"

    # Client S2S
    # spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    # Oauth
    scope = [
        "user-read-playback-state",
        "user-library-read",
        "user-read-currently-playing",
    ]
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    current_queue = spotify.queue()
    print(f"current queue: {current_queue}")

    current_track = spotify.current_playback()
    print(f"current track: {current_track}")

    # results = spotify.artist_albums(birdy_uri, album_type='album')
    # albums = results['items']
    # while results['next']:
    #    results = spotify.next(results)
    #    albums.extend(results['items'])

    # for album in albums:
    #    print(album['name'])
