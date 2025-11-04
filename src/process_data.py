import argparse
import pandas as pd


def merge_and_compute_mood(metadata_path: str, features_path: str) -> pd.DataFrame:
    """
    Merge Spotify metadata (from API) with public audio features (Kaggle 2019)
    and compute the Mood Index.
    """
    print("📥 Loading input files...")
    meta = pd.read_csv(metadata_path)
    feats = pd.read_csv(features_path)

    meta.columns = [c.strip().lower() for c in meta.columns]
    feats.columns = [c.strip().lower() for c in feats.columns]

    print(f"✅ Metadata: {len(meta)} rows, Audio features: {len(feats)} rows")

    # Merge by track_id (inner join: keep only matched songs)
    merged = pd.merge(meta, feats, on="track_id", how="inner")

    if merged.empty:
        print("⚠️ No matching tracks found. Check that song IDs exist in both datasets.")
        return merged

    # Compute Mood Index
    merged["mood_index"] = (merged["valence"] + merged["energy"]) / 2

    # Keep selected columns for clarity
    keep_cols = [
        "track_name_x", "artist_name_x", "country", "date",
        "valence", "energy", "danceability", "tempo",
        "mood_index", "track_popularity", "artist_popularity",
        "artist_genres"
    ]
    merged = merged[keep_cols].rename(columns={
        "track_name_x": "track_name",
        "artist_name_x": "artist_name"
    })

    print(f"✅ Merged dataset: {len(merged)} tracks with audio features.")
    return merged


def main():
    parser = argparse.ArgumentParser(description="Merge Spotify metadata with audio features and compute Mood Index.")
    parser.add_argument("--meta", required=True, help="Path to metadata CSV (from fetch_metadata.py)")
    parser.add_argument("--features", required=True, help="Path to audio features CSV (from load_public_data.py)")
    parser.add_argument("--out", required=True, help="Output CSV file path (processed data)")
    args = parser.parse_args()

    df = merge_and_compute_mood(args.meta, args.features)

    if df.empty:
        print("❌ No data to save (merge produced 0 rows).")
        return

    df.to_csv(args.out, index=False)
    print(f"💾 Saved processed data to: {args.out}")


if __name__ == "__main__":
    main()
