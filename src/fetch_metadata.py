import argparse
from typing import Optional
import time

import pandas as pd
from tqdm import tqdm
from spotipy import Spotify
from spotipy.exceptions import SpotifyException

from utils import get_spotify_client


def search_track_id(sp: Spotify, track_name: str, artist_name: str) -> Optional[str]:
    query = f"track:{track_name} artist:{artist_name}"
    try:
        results = sp.search(q=query, type="track", limit=1)
    except SpotifyException as e:
        print(f"⚠️ Error searching '{track_name}' by '{artist_name}': {e}")
        return None
    items = results.get("tracks", {}).get("items", [])
    return items[0]["id"] if items else None


def build_metadata_row_by_id(sp: Spotify, track_id: str, country: str, date: str) -> Optional[dict]:
    try:
        track = sp.track(track_id)
    except SpotifyException as e:
        print(f"⚠️ Error fetching track {track_id}: {e}")
        return None

    if not track.get("artists"):
        return None
    main_artist = track["artists"][0]
    artist_id = main_artist["id"]

    try:
        artist = sp.artist(artist_id)
    except SpotifyException as e:
        print(f"⚠️ Error fetching artist {artist_id}: {e}")
        return None

    return {
        "track_id": track_id,
        "artist_id": artist_id,
        "track_name": track.get("name"),
        "artist_name": main_artist.get("name"),
        "album_name": track.get("album", {}).get("name"),
        "album_release_date": track.get("album", {}).get("release_date"),
        "track_popularity": track.get("popularity"),
        "artist_popularity": artist.get("popularity"),
        "artist_followers": artist.get("followers", {}).get("total"),
        "artist_genres": "; ".join(artist.get("genres", [])),
        "country": country,
        "date": date,
    }


def build_metadata_row_by_search(sp: Spotify, track_name: str, artist_name: str, country: str, date: str) -> Optional[dict]:
    track_id = search_track_id(sp, track_name, artist_name)
    if track_id is None:
        print(f"❌ Not found on Spotify: '{track_name}' – '{artist_name}'")
        return None
    return build_metadata_row_by_id(sp, track_id, country, date)


def enrich_with_metadata(sp: Spotify, chart_df: pd.DataFrame, country: str, date: str) -> pd.DataFrame:
    chart_df.columns = [c.strip().lower() for c in chart_df.columns]
    rows: list[dict] = []

    # columnas extra que queremos arrastrar desde el chart (de momento, streams del día)
    extra_cols = []
    if "streams_chart" in chart_df.columns:
        extra_cols.append("streams_chart")

    has_id = "track_id" in chart_df.columns

    for _, row in tqdm(chart_df.iterrows(), total=len(chart_df), desc="Fetching metadata"):
        if has_id and pd.notna(row["track_id"]):
            meta = build_metadata_row_by_id(sp, str(row["track_id"]), country, date)
        else:
            track_name = str(row["track_name"])
            artist_name = str(row["artist_name"])
            meta = build_metadata_row_by_search(sp, track_name, artist_name, country, date)

        if meta is not None:
            # copiar columnas extra desde el chart a la salida
            for c in extra_cols:
                val = row.get(c)
                # si hay NaN, lo dejamos como None para no romper tipos
                meta[c] = None if pd.isna(val) else val
            rows.append(meta)

        # pequeñísima pausa para evitar 429 (rate limit)
        time.sleep(0.15)

    return pd.DataFrame(rows) if rows else pd.DataFrame()



def main():
    parser = argparse.ArgumentParser(description="Fetch real Spotify metadata for a list of tracks.")
    parser.add_argument("--chart", required=True, help="CSV with columns [track_name, artist_name] or with [track_id].")
    parser.add_argument("--country", required=True, help="Country name (stored as metadata column)")
    parser.add_argument("--date", required=True, help="Date string (stored as metadata column)")
    parser.add_argument("--out", required=True, help="Output CSV file path for the enriched metadata")
    args = parser.parse_args()

    sp = get_spotify_client()
    chart_df = pd.read_csv(args.chart)
    df_out = enrich_with_metadata(sp, chart_df, country=args.country, date=args.date)

    if df_out.empty:
        print("⚠️ No tracks could be resolved. Check your input file.")
        return

    df_out.to_csv(args.out, index=False)
    print(f"✅ Saved: {args.out} ({len(df_out)} rows)")


if __name__ == "__main__":
    main()
