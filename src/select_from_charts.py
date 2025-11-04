import argparse
import pandas as pd
import re

def extract_track_id(url: str):
    if not isinstance(url, str):
        return None
    # Ejemplos: https://open.spotify.com/track/7qiZfU4dY1lWllzX7mPBI3  |  spotify:track:7qiZfU4dY1lWllzX7mPBI3
    m = re.search(r"(track/|track:)([0-9A-Za-z]{22})", url)
    return m.group(2) if m else None

def normalize_country(s: str) -> str:
    return (s or "").strip().lower()

def pick_sample(df: pd.DataFrame, country: str, date: str, top_n: int) -> pd.DataFrame:
    # Normaliza columnas para soportar variantes
    df.columns = [c.strip().lower() for c in df.columns]

    # Mapear posibles nombres de columnas
    col_track  = "track name" if "track name" in df.columns else ("trackname" if "trackname" in df.columns else "track")
    col_artist = "artist" if "artist" in df.columns else ("artist name" if "artist name" in df.columns else "artists")
    col_url    = "url"
    col_date   = "date"
    col_region = "region"
    col_pos    = "position"

    # Filtro por país (acepta ES / Spain / es / spain)
    country_norm = normalize_country(country)
    df = df[df[col_region].apply(lambda x: normalize_country(x) in {country_norm, country_norm[:2]})]

    # Filtro por fecha exacta (YYYY-MM-DD)
    df = df[df[col_date] == date]

    # Extrae track_id desde la URL
    df["track_id"] = df[col_url].apply(extract_track_id)

    # Ordena por posición y toma Top-N con columnas limpias
    out = (
        df.sort_values(col_pos)
          .head(top_n)
          .loc[:, [col_track, col_artist, "track_id", col_date, col_region]]
          .rename(columns={
              col_track: "track_name",
              col_artist: "artist_name",
              col_date: "date",
              col_region: "country"
          })
          .dropna(subset=["track_id"])
          .reset_index(drop=True)
    )
    return out

def main():
    ap = argparse.ArgumentParser(description="Select Top-N daily chart for a country/date and extract track_id.")
    ap.add_argument("--input", required=True, help="Path to worldwide daily charts CSV")
    ap.add_argument("--country", required=True, help="Country name or code (e.g., Spain or ES)")
    ap.add_argument("--date", required=True, help="Date YYYY-MM-DD (use one present in the dataset)")
    ap.add_argument("--top", type=int, default=20, help="Top-N songs (default: 20)")
    ap.add_argument("--out", required=True, help="Output CSV, e.g. data/raw/spain_sample_2017-08-01.csv")
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    sample = pick_sample(df, args.country, args.date, args.top)

    if sample.empty:
        print("⚠️ No se han encontrado canciones para ese país/fecha (o no hay URLs válidas).")
        return

    sample.to_csv(args.out, index=False)
    print(f"✅ Saved sample: {args.out} ({len(sample)} rows)")

if __name__ == "__main__":
    main()
