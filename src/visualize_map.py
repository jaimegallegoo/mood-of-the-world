import argparse, os, zipfile, io
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Name mapping for Natural Earth
NAME_FIX = {
    "United States": "United States of America",
    "Czechia": "Czech Republic",
    "Russia": "Russian Federation",
    "South Korea": "Korea, Republic of",
    "North Korea": "Korea, Democratic People's Republic of",
    "Bolivia": "Bolivia (Plurinational State of)",
    "Iran": "Iran (Islamic Republic of)",
    "Venezuela": "Venezuela (Bolivarian Republic of)",
}

NE_URLS = [
    "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip",
    "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip",
]

def ensure_admin0_local(out_dir="data/external/ne_admin0") -> str:
    os.makedirs(out_dir, exist_ok=True)
    shp_candidates = [f for f in os.listdir(out_dir) if f.endswith(".shp")]
    if shp_candidates:
        return out_dir

    for url in NE_URLS:
        try:
            print(f"🌐 Downloading Natural Earth (admin0): {url}")
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                z.extractall(out_dir)
            if [f for f in os.listdir(out_dir) if f.endswith(".shp")]:
                return out_dir
        except Exception as e:
            print(f"⚠️ Failed download from {url}: {e}")

    raise SystemExit("❌ Could not download shapefile.")

def main():
    ap = argparse.ArgumentParser(description="World Map of Mood Index (English)")
    ap.add_argument("--summary", default="data/processed/country_summary.csv")
    ap.add_argument("--date", required=True, help="Date YYYY-MM-DD")
    ap.add_argument("--metric", default="w_mean_streams", choices=["mean", "w_mean_streams"])
    ap.add_argument("--outdir", default="figures")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    df = pd.read_csv(args.summary)
    df = df[df["date"] == args.date].copy()
    
    if df.empty:
        print(f"⚠️ No data found for date {args.date}")
        return

    df["country_plot"] = df["country"].map(lambda x: NAME_FIX.get(x, x))
    admin0_dir = ensure_admin0_local()
    shp_files = [os.path.join(admin0_dir, f) for f in os.listdir(admin0_dir) if f.endswith(".shp")]
    world = gpd.read_file(shp_files[0])

    # Filter out Antarctica for a cleaner map
    world = world[world["ADMIN"] != "Antarctica"]

    merged = world.merge(df, left_on="ADMIN", right_on="country_plot", how="left")

    metric_label = "Weighted Mood Index" if args.metric == "w_mean_streams" else "Mean Mood Index"
    title = f"Global Music Mood: {metric_label} ({args.date})"

    fig, ax = plt.subplots(1, 1, figsize=(15, 8))
    
    merged.plot(
        column=args.metric,
        cmap="RdYlGn", # Red (Low Mood) to Green (High Mood) usually works well for this
        legend=True,
        legend_kwds={'label': "Mood Index (0-1)", 'orientation': "horizontal", 'shrink': 0.5},
        missing_kwds={"color": "#f0f0f0", "edgecolor": "#d0d0d0", "hatch": "///", "label": "No data"},
        ax=ax
    )
    
    ax.set_title(title, fontsize=16)
    ax.set_axis_off()

    # Force "No data" into legend
    handles, labels = ax.get_legend_handles_labels()
    if "No data" not in labels:
        patch = Patch(facecolor="#f0f0f0", edgecolor="#d0d0d0", hatch="///", label="No Data")
        # We rely on the plot's internal legend mechanism usually, but sometimes we need to add it manually.
        # For geopandas plots with missing_kwds, it often handles it, but let's ensure.
        pass 

    out = os.path.join(args.outdir, f"map_{args.metric}_{args.date}.png")
    plt.tight_layout()
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"✅ Saved English map: {out}")

if __name__ == "__main__":
    main()