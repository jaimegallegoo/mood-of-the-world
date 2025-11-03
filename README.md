# Mood of the World

## Project Description
"Mood of the World" is a data-driven project that analyzes emotional trends in popular music worldwide using Spotify data. By combining Spotify Top Charts datasets with the Spotify Web API, the project extracts audio features such as valence, energy, tempo, and popularity to compute a Mood Index for each country and time period. The results are visualized to reveal cultural and seasonal mood patterns.

## Goals
- Compute a Mood Index = (valence + energy) / 2 for each country and time period (week/month).
- Visualize results to uncover cultural and seasonal mood patterns (e.g., summer vs. winter).
- Generate insights through global heat maps, seasonal comparisons, and scatter plots.

## Repository Structure
```
mood-of-the-world/
├─ data/          # Datasets (ignored by Git)
├─ notebooks/     # Jupyter notebooks
├─ src/
│  ├─ fetch_data.py    -> Retrieve songs + audio features from Spotify
│  ├─ process_data.py  -> Compute Mood Index
│  └─ visualize.py     -> Create charts and maps
├─ figures/       # Generated plots (ignored)
├─ paper/         # Academic report (ignored)
├─ requirements.txt
├─ .gitignore
└─ .env
```

## Technical Setup
- **Language**: Python 3
- **Libraries**: spotipy, pandas, numpy, matplotlib, seaborn, plotly, geopandas, requests, tqdm, python-dotenv
- **API**: Spotify Web API (Client ID & Secret stored in `.env`)
- **Outputs**: CSV files + visualizations (heat maps, line plots, scatter plots)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/jaimegallegoo/mood-of-the-world.git
   ```
2. Navigate to the project directory:
   ```bash
   cd mood-of-the-world
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Set up your Spotify API credentials in a `.env` file:
   ```
   SPOTIPY_CLIENT_ID=your_client_id
   SPOTIPY_CLIENT_SECRET=your_client_secret
   ```
2. Run the scripts in the `src/` directory to fetch, process, and visualize data.
3. Explore the results in the `figures/` directory or through Jupyter notebooks in the `notebooks/` directory.

## Expected Results
- **Global Heat Map**: Average Mood Index per country.
- **Seasonal Comparison**: Mood patterns in summer vs. winter, north vs. south hemisphere.
- **Scatter Plots**: Comparing valence and energy by region.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Spotify Web API for providing the data.
- Libraries and tools used in this project.
- TU Wien for supporting this research initiative.