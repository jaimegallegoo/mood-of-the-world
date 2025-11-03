import os
import time
import argparse
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException


# ----------------------------------------------------------
#  Spotify Authentication
# ----------------------------------------------------------
def get_spotify_client() -> spotipy.Spotify:
    """
    Create and return a Spotify client using Client Credentials Flow.
    Environment variables must include:
        - SPOTIPY_CLIENT_ID
        - SPOTIPY_CLIENT_SECRET
        - SPOTIPY_REDIRECT_URI
    """
    load_dotenv()
    cid = os.getenv("SPOTIPY_CLIENT_ID")
    secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    if not cid or not secret:
        raise RuntimeError("Missing SPOTIPY_CLIENT_ID or SPOTIPY_CLIENT_SECRET in .env file")

    auth_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    return spotipy.Spotify(auth_manager=auth_manager, requests_timeout=20, retries=3)


# ----------------------------------------------------------
#  Search and Audio Features Retrieval
# ----------------------------------------------------------
def search_track_id(sp: spotipy.Spotify, track_name: str, artist_name: str) -> str | None:
    """
    Search for a Spotify track ID using track name and artist name.
    Returns None if the track is not found.
    """
    query = f"track:{track_name} artist:{artist_name}"
    results = sp.search(q=query, type="track", limit=1)
    items = results.get("tracks", {}).get("items", [])
    return items[0]["id"] if items else None


def get_audio_features(sp: spotipy.Spotify, track_ids: list[str]) -> pd.DataFrame:
    """
    Retrieve Spotify audio features for a list of track IDs.
    Handles batching (max 100 IDs per request, 50 used here for safety).
    """
    features = []
    for batch_start in range(0, len(track_ids), 50):
        ids = track_ids[batch_start:batch_start + 50]
        feats = sp.audio_features(ids)
        features.extend(feats)
    df = pd.DataFrame(features)
    return df


# ----------------------------------------------------------
#  Main Processing Pipeline
# ----------------------------------------------------------
def enrich_chart_with_features(sp: spotipy.Spotify,
                               chart_df: pd.DataFrame,
                               country: str = "Spain",
                               date: str | None = None) -> pd.DataFrame:
    """
    Takes a CSV with columns [track_name, artist_name],
    searches for Spotify track IDs, retrieves audio features,
    and computes the Mood Index for each track.
    """
    track_ids = []
    for _, row in tqdm(chart_df.iterrows(), total=len(chart_df), desc="Searching tracks"):
        tid = search_track_id(sp, row["track_name"], row["artist_name"])
        track_ids.append(tid)

    chart_df["track_id"] = track_ids
    chart_df = chart_df.dropna(subset=["track_id"]).reset_index(drop=True)

    feats = get_audio_features(sp, chart_df["track_id"].tolist())
    result = chart_df.merge(feats, left_on="track_id", right_on="id", how="left")

    # Compute Mood Index
    result["MoodIndex"] = (result["valence"] + result["energy"]) / 2
    result["country"] = country
    result["date"] = date

    return result


# ----------------------------------------------------------
#  Command-line Interface
# ----------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Enrich a CSV with Spotify audio features and Mood Index")
    parser.add_argument("--chart", required=True, help="Path to input CSV with columns [track_name, artist_name]")
    parser.add_argument("--country", default="Spain", help="Country name (for metadata)")
    parser.add_argument("--date", default="2024-10-01", help="Date string (for metadata)")
    parser.add_argument("--out", required=True, help="Output CSV file path")
    args = parser.parse_args()

    sp = get_spotify_client()
    df = pd.read_csv(args.chart)
    df_out = enrich_chart_with_features(sp, df, country=args.country, date=args.date)
    df_out.to_csv(args.out, index=False)
    print(f"✅ Saved: {args.out} ({len(df_out)} rows)")


if __name__ == "__main__":
    main()
