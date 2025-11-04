import subprocess
from pathlib import Path
import sys

# === Configura aquí tus países/fechas (ajusta si alguna fecha no existe en el CSV de charts) ===
TASKS = [
    {"cc": "ES", "country": "Spain", "date": "2017-08-01", "top": 50},
    {"cc": "ES", "country": "Spain", "date": "2018-01-05", "top": 50},
    {"cc": "FR", "country": "France", "date": "2017-08-01", "top": 50},
    {"cc": "FR", "country": "France", "date": "2018-01-05", "top": 50},
    {"cc": "DE", "country": "Germany", "date": "2017-08-01", "top": 50},
    {"cc": "DE", "country": "Germany", "date": "2018-01-05", "top": 50},
    {"cc": "US", "country": "United States", "date": "2017-08-01", "top": 50},
    {"cc": "US", "country": "United States", "date": "2018-01-05", "top": 50},
    # {"cc": "BR", "country": "Brazil", "date": "2017-08-01", "top": 50},
    # {"cc": "BR", "country": "Brazil", "date": "2018-01-05", "top": 50},
]

CHARTS_PATH = "data/raw/worldwide_daily_song_ranking.csv"
FEATURES_CLEAN = "data/interim/audio_features_clean.csv"

PY = sys.executable  # << usa el python del venv actual

def run(cmd):
    print(">>", " ".join(cmd))
    subprocess.run(cmd, check=True)

def main():
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/interim").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)

    for t in TASKS:
        cc = t["cc"]; cn = t["country"]; date = t["date"]; top = str(t["top"])

        sample_csv = f"data/raw/{cc}_sample_{date}.csv"
        meta_csv   = f"data/interim/{cc}_metadata_{date}.csv"
        out_csv    = f"data/processed/{cc}_mood_{date}.csv"

        # 1) Select Top-N from charts
        run([PY, "src/select_from_charts.py",
             "--input", CHARTS_PATH,
             "--country", cc,
             "--date", date,
             "--top", top,
             "--out", sample_csv])

        # 2) Enrich via API
        run([PY, "src/fetch_metadata.py",
             "--chart", sample_csv,
             "--country", cn,
             "--date", date,
             "--out", meta_csv])

        # 3) Merge + MoodIndex
        run([PY, "src/process_data.py",
             "--meta", meta_csv,
             "--features", FEATURES_CLEAN,
             "--out", out_csv])

    print("✅ Multi-país completado.")

if __name__ == "__main__":
    main()
