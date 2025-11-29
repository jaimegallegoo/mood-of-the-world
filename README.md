# Mood of the World

A data science project to analyze the global emotional "mood" of music using Spotify data.

This project estimates a **Mood Index** per country and time period by combining:
- **Spotify API metadata**: Tracks and artists info (genres, popularity).
- **Public audio features**: A dataset with valence, energy, danceability, and tempo.
- **Daily Charts**: Streaming data per country to weight the impact of each song.

We compute `MoodIndex = (valence + energy) / 2`, aggregate by country/date, and visualize seasonal trends.

---

## Project Structure

```
mood-of-the-world/
├── data/
│   ├── raw/        # Input CSVs (charts, public features)
│   ├── interim/    # API metadata (fetched per country)
│   └── processed/  # Final merged datasets + country_summary.csv
├── figures/        # Generated charts and maps
├── src/            # Python scripts
├── requirements.txt
└── README.md
```

---

## Requirements

- Python 3.10+
- A Spotify App (Client ID/Secret) for Development mode.

**Setup:**
```powershell
python -m venv venv
& ./venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file with your credentials:

```
SPOTIPY_CLIENT_ID=your_id
SPOTIPY_CLIENT_SECRET=your_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

---

## Workflow

### 1. Data Preparation

Clean the public audio features dataset (Kaggle snapshot):

```powershell
python src/load_public_data.py --input data/raw/SpotifyAudioFeaturesApril2019.csv --out data/interim/audio_features_clean.csv
```

### 2. Execution (Multi-Country)

Run the main pipeline. This script fetches charts, queries the Spotify API for metadata (handling rate limits), and merges data for 8 countries across Europe, America, Asia, and Oceania.

```powershell
python src/multi_country_run.py
```

### 3. Summarization

Aggregate KPIs (Mood Index, Match Rate, Streams) into a summary CSV:

```powershell
python src/summarize.py
```

### 4. Visualization

Generate the final figures for the report (English labels):

**Seasonal Comparison (Key Chart):**

```powershell
python src/visualize_seasonal.py
```

**World Maps (Summer/Winter):**

```powershell
python src/visualize_map.py --date 2017-08-01 --metric w_mean_streams
python src/visualize_map.py --date 2018-01-05 --metric w_mean_streams
```

**Country Rankings:**

```powershell
python src/visualize_countries.py
```

All figures are saved in the `figures/` directory.

---

## Methodology Notes

- **Hybrid Approach**: Due to Spotify API restrictions on audio-features (403 Forbidden), we fetch metadata via API but retrieve valence/energy from a public dataset using robust name matching.

- **Metrics**: The `w_mean_streams` metric weights the Mood Index by the number of streams in the daily chart, offering a more realistic representation of what people are actually listening to.

---

## License

MIT License.
