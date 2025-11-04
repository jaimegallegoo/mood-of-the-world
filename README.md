# Mood of the World

A lightweight pipeline to estimate a country-level **Mood Index** of music by combining:
- **Spotify API metadata** (tracks/artists: popularity, genres, followers),
- **Public audio features** (valence, energy, danceability, tempo),
- **Daily country charts** (streams per track).

We compute `MoodIndex = (valence + energy) / 2`, aggregate by country/date, and produce bar charts, coverage charts, and a world map.

---

## Requirements

- Python 3.10+
- A Spotify app (client id/secret) for Development mode

Create and activate a virtual environment, then install deps:

```powershell
python -m venv venv
& ./venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

Minimal `requirements.txt` (you may pin versions):

```
spotipy
pandas
numpy
matplotlib
geopandas
requests
tqdm
python-dotenv
```

Create a `.env` file in the project root:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8080
```

---

## Data

- **Charts (2017–2018):** `data/raw/worldwide_daily_song_ranking.csv`  
  Columns: `Position, Track Name, Artist, Streams, URL, Date, Region`.

- **Audio features snapshot (public, 2019):** `data/raw/SpotifyAudioFeaturesApril2019.csv`.

---

## Quick Start (PowerShell)

1) **Clean & load features**
```powershell
python src/load_public_data.py --input data/raw/SpotifyAudioFeaturesApril2019.csv --out data/interim/audio_features_clean.csv
```

2) **Run multi-country pipeline**  
Edit `TASKS` inside `src/multi_country_run.py` (countries/dates), then:
```powershell
python src/multi_country_run.py
```
This produces:
- `data/raw/{CC}_sample_{DATE}.csv` (Top-N chart with `track_id` + `streams_chart`)
- `data/interim/{CC}_metadata_{DATE}.csv` (API metadata)
- `data/processed/{CC}_mood_{DATE}.csv` (merged + `mood_index`)

3) **Summarize KPIs across countries**
```powershell
python src/summarize.py
```
Output: `data/processed/country_summary.csv` with:
- `n_chart, n_matched, match_rate`
- `mean, median, p25, p75`
- `w_mean_pop` (weighted by popularity) and `w_mean_streams` (weighted by chart streams)

4) **Visualizations**
- Single set (one processed CSV):
```powershell
python src/visualize.py --input data/processed/ES_mood_2017-08-01.csv --outdir figures
```
- Country comparison (bars + coverage per date):
```powershell
python src/visualize_countries.py --summary data/processed/country_summary.csv --outdir figures
```
- World map (first run auto-downloads Natural Earth admin_0):
```powershell
python src/visualize_map.py --date 2017-08-01 --metric mean
python src/visualize_map.py --date 2017-08-01 --metric w_mean_streams
```

---

## What the scripts do

- `select_from_charts.py` – Pick Top-N by country/date from the charts CSV and extract `track_id` from the Spotify URL.  
- `fetch_metadata.py` – Enrich with Spotify API (popularity, artist followers/genres…).  
- `load_public_data.py` – Clean the public features snapshot.  
- `process_data.py` – Merge (by `track_id`, fallback by normalized `(track_name, artist_name)`), compute `mood_index`.  
- `summarize.py` – Aggregate country/date KPIs and coverage (`match_rate`).  
- `visualize.py`, `visualize_countries.py`, `visualize_map.py`, `visualize_compare.py` – Generate charts and maps.

---

## Outputs

- CSVs in `data/processed/` (per country/date and the global `country_summary.csv`).
- Figures in `figures/`:
  - Bars by country (`mean`, `w_mean_streams`),
  - Match rate per country,
  - World map by date/metric,
  - Optional A/B boxplots/scatter for a country (e.g., summer vs winter).

---

## Limitations (short)

- Spotify `/audio-features` is unavailable in Development mode; we rely on a public 2019 snapshot.
- Charts and snapshot may refer to different editions (IDs), so we use a robust name-based fallback.
- Coverage varies by country/date → we report `match_rate`.

---

## Repo Layout

```
mood-of-the-world/
├── data/
│   ├── raw/        # input CSVs (charts, public features)
│   ├── interim/    # API metadata (per country/date)
│   └── processed/  # merged results + summaries
├── figures/        # generated images
├── src/            # scripts
├── paper/          # optional report artifacts
├── requirements.txt
└── README.md
```

---

## Re-run / Clean

- Scripts overwrite outputs with the same `--out`.
- Clean intermediates if needed:
```powershell
Remove-Item data\interim\*_metadata_*.csv -Force -ErrorAction SilentlyContinue
Remove-Item data\processed\*_mood_*.csv   -Force -ErrorAction SilentlyContinue
Remove-Item data\processed\country_summary.csv -Force -ErrorAction SilentlyContinue
Remove-Item figures\*.png -Force -ErrorAction SilentlyContinue
```
