import argparse
from typing import Optional

import pandas as pd
from tqdm import tqdm
from spotipy import Spotify
from spotipy.exceptions import SpotifyException

from utils import get_spotify_client


def search_track_id(sp: Spotify, track_name: str, artist_name: str) -> Optional[str]:
    """
    Search for a Spotify track ID using track name and artist name.
    Returns None if the track is not found.
    """
    query = f"track:{track_name} artist:{artist_name}"
    try:
        results = sp.search(q=query, type="track", limit=1)
    except SpotifyException as e:
        print(f"⚠️ Error searching '{track_name}' by '{artist_name}': {e}")
        return None

    items = results.get("tracks", {}).get("items", [])
    return items[0]["id"] if items else None


def build_metadata_row(sp: Spotify,
                       track_name: str,
                       artist_name: str,
                       country: str,
                       date: str) -> Optional[dict]:
    """
    Given a track name and artist name, search the track on Spotify
    and return a dict with track + artist metadata.
    Returns None if the track cannot be resolved.
    """
    track_id = search_track_id(sp, track_name, artist_name)
    if track_id is None:
        print(f"❌ Not found on Spotify: '{track_name}' – '{artist_name}'")
        return None

    try:
        track = sp.track(track_id)
    except SpotifyException as e:
        print(f"⚠️ Error fetching track {track_id}: {e}")
        return None

    # Take the first artist as the "main" one
    if not track.get("artists"):
        print(f"⚠️ Track {track_id} has no artists field")
        return None

    main_artist = track["artists"][0]
    artist_id = main_artist["id"]

    try:
        artist = sp.artist(artist_id)
    except SpotifyException as e:
        print(f"⚠️ Error fetching artist {artist_id}: {e}")
        return None

    # Build a clean metadata row
    metadata = {
        # Original input (for traceability)
        "track_name_input": track_name,
        "artist_name_input": artist_name,

        # IDs
        "track_id": track_id,
        "artist_id": artist_id,

        # Canonical names from Spotify
        "track_name": track.get("name"),
        "artist_name": main_artist.get("name"),

        # Album info
        "album_name": track.get("album", {}).get("name"),
        "album_release_date": track.get("album", {}).get("release_date"),

        # Popularity
        "track_popularity": track.get("popularity"),
        "artist_popularity": artist.get("popularity"),
        "artist_followers": artist.get("followers", {}).get("total"),

        # Genres (joined as a single string)
        "artist_genres": "; ".join(artist.get("genres", [])),

        # Extra metadata for our project
        "country": country,
        "date": date,
    }

    return metadata


def enrich_with_metadata(sp: Spotify,
                         chart_df: pd.DataFrame,
                         country: str,
                         date: str) -> pd.DataFrame:
    """
    Iterate over an input DataFrame with at least:
      - track_name
      - artist_name

    and return a new DataFrame with Spotify metadata for
    all tracks that could be resolved.
    """
    rows: list[dict] = []

    for _, row in tqdm(chart_df.iterrows(), total=len(chart_df), desc="Fetching metadata"):
        track_name = str(row["track_name"])
        artist_name = str(row["artist_name"])
        meta = build_metadata_row(sp, track_name, artist_name, country, date)
        if meta is not None:
            rows.append(meta)

    if not rows:
        print("⚠️ No tracks could be resolved. Check your input file.")
        return pd.DataFrame()

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch real Spotify metadata for a list of tracks."
    )
    parser.add_argument(
        "--chart",
        required=True,
        help="Path to input CSV with columns [track_name, artist_name]",
    )
    parser.add_argument(
        "--country",
        default="Spain",
        help="Country name (stored as metadata column)",
    )
    parser.add_argument(
        "--date",
        default="2024-10-01",
        help="Date string (stored as metadata column)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output CSV file path for the enriched metadata",
    )
    args = parser.parse_args()

    # 1) Authenticate
    sp = get_spotify_client()

    # 2) Load input CSV (e.g. data/raw/spain_sample.csv)
    chart_df = pd.read_csv(args.chart)

    # 3) Fetch metadata
    df_out = enrich_with_metadata(sp, chart_df, country=args.country, date=args.date)

    # 4) Save result
    df_out.to_csv(args.out, index=False)
    print(f"✅ Saved: {args.out} ({len(df_out)} rows)")


if __name__ == "__main__":
    main()
