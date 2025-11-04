import pandas as pd
import numpy as np
from pathlib import Path
import glob
import os
import re

IN_PATTERN = "data/processed/*_mood_*.csv"
OUT_PATH   = "data/processed/country_summary.csv"

def weighted_mean(x, w):
    x = pd.to_numeric(x, errors="coerce")
    w = pd.to_numeric(w, errors="coerce")
    m = (x * w).sum()
    s = w.sum()
    return float(m / s) if s and s > 0 else np.nan

def infer_metadata_path(processed_path: str) -> str | None:
    """
    processed: data/processed/ES_mood_2017-08-01.csv
    -> interim: data/interim/ES_metadata_2017-08-01.csv (si existe)
    """
    # Usar solo el nombre del archivo para evitar problemas de separadores (\ vs /)
    fname = Path(processed_path).name  # p.ej., "ES_mood_2017-08-01.csv"
    m = re.match(r"^([A-Za-z]{2})_mood_(\d{4}-\d{2}-\d{2})\.csv$", fname)
    if not m:
        return None
    cc, date = m.group(1).upper(), m.group(2)
    candidate = Path("data/interim") / f"{cc}_metadata_{date}.csv"
    return str(candidate) if candidate.exists() else None

def summarize_file(path):
    df = pd.read_csv(path)
    if df.empty:
        return None

    for col in ["country", "date", "mood_index"]:
        if col not in df.columns:
            return None

    country = str(df["country"].iloc[0])
    date    = str(df["date"].iloc[0])

    # coverage
    n_matched = int(len(df))
    meta_path = infer_metadata_path(path)
    if meta_path:
        try:
            n_chart = int(len(pd.read_csv(meta_path)))
        except Exception:
            n_chart = np.nan
    else:
        n_chart = np.nan

    match_rate = float(n_matched / n_chart) if isinstance(n_chart, (int, float)) and n_chart and n_chart > 0 else np.nan

    # mood stats
    mood = pd.to_numeric(df["mood_index"], errors="coerce").dropna()
    if mood.empty:
        return {
            "country": country, "date": date,
            "n_chart": n_chart, "n_matched": n_matched, "match_rate": match_rate,
            "mean": np.nan, "median": np.nan, "p25": np.nan, "p75": np.nan,
            "w_mean_pop": np.nan, "w_mean_streams": np.nan
        }

    mean   = float(mood.mean())
    median = float(mood.median())
    p25, p50, p75 = np.percentile(mood, [25, 50, 75])

    # ponderación por popularidad (si existe)
    if "track_popularity" in df.columns:
        w_pop = np.clip(pd.to_numeric(df["track_popularity"], errors="coerce"), 0, 100) / 100.0
        w_mean_pop = weighted_mean(df["mood_index"], w_pop)
    else:
        w_mean_pop = np.nan

    # ponderación por streams del chart (si existe)
    if "streams_chart" in df.columns:
        w_streams = pd.to_numeric(df["streams_chart"], errors="coerce").clip(lower=0)
        w_mean_streams = weighted_mean(df["mood_index"], w_streams)
    else:
        w_mean_streams = np.nan

    return {
        "country": country, "date": date,
        "n_chart": n_chart, "n_matched": n_matched, "match_rate": match_rate,
        "mean": mean, "median": float(median), "p25": float(p25), "p75": float(p75),
        "w_mean_pop": w_mean_pop, "w_mean_streams": w_mean_streams
    }

def main():
    rows = []
    for path in glob.glob(IN_PATTERN):
        row = summarize_file(path)
        if row is not None:
            rows.append(row)

    if not rows:
        print("⚠️ No processed files found.")
        return

    out = pd.DataFrame(rows).sort_values(["date", "country"]).reset_index(drop=True)
    Path(OUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False)
    print(f"✅ Saved summary: {OUT_PATH} ({len(out)} rows)")

if __name__ == "__main__":
    main()
