import argparse
import pandas as pd
import unicodedata
import re


def norm_text(s: str) -> str:
    s = "" if s is None else str(s)
    s = s.lower()
    # quitar acentos
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    # eliminar "feat. ..." y paréntesis con feats
    s = re.sub(r"\s*\(feat\.?[^)]*\)", "", s)
    s = re.sub(r"\s*feat\.?.*$", "", s)
    # solo letras/numeros/espacios
    s = re.sub(r"[^a-z0-9 ]+", "", s)
    # espacios compactados
    s = re.sub(r"\s+", " ", s).strip()
    return s


def merge_and_compute_mood(metadata_path: str, features_path: str) -> pd.DataFrame:
    print("📥 Loading input files...")
    meta = pd.read_csv(metadata_path)
    feats = pd.read_csv(features_path)

    meta.columns = [c.strip().lower() for c in meta.columns]
    feats.columns = [c.strip().lower() for c in feats.columns]

    print(f"✅ Metadata: {len(meta)} rows, Audio features: {len(feats)} rows")

    # ---------- 1) Merge por track_id ----------
    merged_id = pd.DataFrame()
    if "track_id" in meta.columns and "track_id" in feats.columns:
        merged_id = pd.merge(meta, feats, on="track_id", how="inner")
        print(f"🔗 ID-merge matches: {len(merged_id)}")

    # ---------- 2) Merge por (track_name, artist_name) normalizados ----------
    matched_ids = set(merged_id["track_id"]) if not merged_id.empty and "track_id" in merged_id.columns else set()
    meta_unmatched = meta[~meta["track_id"].isin(matched_ids)] if "track_id" in meta.columns else meta.copy()

    for df in (meta_unmatched, feats):
        if "track_name" in df.columns and "artist_name" in df.columns:
            df["t_norm"] = df["track_name"].map(norm_text)
            df["a_norm"] = df["artist_name"].map(norm_text)

    merged_name = pd.DataFrame()
    if {"t_norm", "a_norm"}.issubset(set(meta_unmatched.columns)) and {"t_norm", "a_norm"}.issubset(set(feats.columns)):
        merged_name = pd.merge(
            meta_unmatched,
            feats,
            on=["t_norm", "a_norm"],
            how="inner",
            suffixes=("_meta", "_feat"),
        )
        print(f"🧩 Name-merge matches: {len(merged_name)}")

    # ---------- 3) Unir resultados y calcular MoodIndex ----------
    merged = pd.concat([merged_id, merged_name], ignore_index=True, sort=False).drop_duplicates()
    if merged.empty:
        print("⚠️ No matching tracks found after ID + name merges.")
        return merged

    for col in ["valence", "energy"]:
        if col not in merged.columns:
            merged[col] = pd.NA

    merged["valence"] = merged["valence"].astype(float)
    merged["energy"]  = merged["energy"].astype(float)
    merged["mood_index"] = (merged["valence"] + merged["energy"]) / 2

    pick = [
        "track_name_meta" if "track_name_meta" in merged.columns else "track_name",
        "artist_name_meta" if "artist_name_meta" in merged.columns else "artist_name",
        "country", "date",
        "valence", "energy", "danceability", "tempo",
        "mood_index", "track_popularity", "artist_popularity", "artist_genres"
    ]
    keep_cols = [c for c in pick if c in merged.columns]
    merged = merged[keep_cols].rename(columns={
        "track_name_meta": "track_name",
        "artist_name_meta": "artist_name"
    })

    print(f"✅ Final merged dataset: {len(merged)} rows.")
    return merged


def main():
    ap = argparse.ArgumentParser(description="Merge Spotify metadata with audio features (ID + name fallback) and compute Mood Index.")
    ap.add_argument("--meta", required=True, help="Path to metadata CSV (from fetch_metadata.py)")
    ap.add_argument("--features", required=True, help="Path to audio features CSV (from load_public_data.py)")
    ap.add_argument("--out", required=True, help="Output CSV file path")
    args = ap.parse_args()

    df = merge_and_compute_mood(args.meta, args.features)
    if df.empty:
        print("❌ No data to save (merge produced 0 rows).")
        return

    df.to_csv(args.out, index=False)
    print(f"💾 Saved processed data to: {args.out}")


if __name__ == "__main__":
    main()
