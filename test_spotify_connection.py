from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import os
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
    )
)

# Prueba básica: buscar un artista
results = sp.search(q="Rosalía", type="artist", limit=1)

artist = results["artists"]["items"][0]["name"]
print(f"✅ Conexión correcta. Primer artista encontrado: {artist}")
