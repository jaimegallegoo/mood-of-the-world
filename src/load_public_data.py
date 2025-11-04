import argparse
import pandas as pd


def load_public_audio_features(path: str) -> pd.DataFrame:
    """
    Load and clean the public Spotify audio features dataset (e.g. TomiGelo April 2019).
    Keeps only relevant columns for Mood of the World analysis.
    """
    print(f"📥 Loading dataset: {path}")
    df = pd.read_csv(path)

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    expected_cols = [
        "track_id", "track_name", "artist_name", "popularity",
        "danceability", "energy", "valence", "tempo"
    ]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    # Keep only the relevant ones
    df_clean = df[expected_cols].drop_duplicates(subset="track_id").reset_index(drop=True)

    print(f"✅ Loaded {len(df_clean):,} tracks after cleaning.")
    return df_clean


def main():
    parser = argparse.ArgumentParser(
        description="Load and clean the public Spotify Audio Features dataset."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to raw CSV (e.g. data/raw/SpotifyAudioFeaturesApril2019.csv)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Path to save cleaned dataset (e.g. data/interim/audio_features_clean.csv)",
    )
    args = parser.parse_args()

    df = load_public_audio_features(args.input)
    df.to_csv(args.out, index=False)
    print(f"💾 Saved cleaned dataset to: {args.out}")


if __name__ == "__main__":
    main()
