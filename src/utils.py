import os
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyOAuth


def get_spotify_client() -> spotipy.Spotify:
    """
    Create and return a Spotify client using Authorization Code Flow.
    This requires a one-time login in the browser.
    """
    load_dotenv()
    cid = os.getenv("SPOTIPY_CLIENT_ID")
    secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect = os.getenv("SPOTIPY_REDIRECT_URI")

    if not cid or not secret or not redirect:
        raise RuntimeError("Missing Spotify credentials in .env file")

    auth_manager = SpotifyOAuth(
        client_id=cid,
        client_secret=secret,
        redirect_uri=redirect,
        # For our use case (search, tracks, artists) no special scopes are needed,
        # but we keep a simple read scope.
        scope="user-read-private"
    )

    return spotipy.Spotify(auth_manager=auth_manager)
