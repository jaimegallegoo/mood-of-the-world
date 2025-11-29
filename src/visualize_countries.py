import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_bar(d: pd.DataFrame, col: str, title: str, ylabel: str, out_path: str, ylim01=False):
    plt.figure(figsize=(10,6)) # Slightly larger for English labels
    # Sort by value for better readability
    d_sorted = d.sort_values(col, ascending=False)
    
    plt.bar(d_sorted["country"], d_sorted[col], color="skyblue", edgecolor="black")
    plt.title(title, fontsize=14)
    plt.ylabel(ylabel, fontsize=12)
    plt.xlabel("Country", fontsize=12)
    
    if ylim01:
        plt.ylim(0, 1)
    else:
        # Dynamic limit for Mood Index to show contrast
        plt.ylim(0.4, 0.8)

    plt.xticks(rotation=45, ha="right")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"✅ Saved: {out_path}")

def main():
    ap = argparse.ArgumentParser(description="Multi-country visualizations (English)")
    ap.add_argument("--summary", default="data/processed/country_summary.csv")
    ap.add_argument("--outdir", default="figures")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    df = pd.read_csv(args.summary)

    for date in sorted(df["date"].unique()):
        d = df[df["date"] == date].copy()

        # 1) Simple Mean
        out1 = os.path.join(args.outdir, f"mood_by_country_mean_{date}.png")
        plot_bar(d, "mean", f"Average Mood Index by Country ({date})",
                 "Mood Index (Simple Mean)", out1)

        # 2) Weighted Mean (Streams) - This is the main one for the paper
        out2 = os.path.join(args.outdir, f"mood_by_country_wstreams_{date}.png")
        plot_bar(d, "w_mean_streams", f"Stream-Weighted Mood Index ({date})",
                 "Mood Index (Weighted by Streams)", out2)

        # 3) Match Rate
        out3 = os.path.join(args.outdir, f"match_rate_{date}.png")
        plot_bar(d, "match_rate", f"Data Coverage / Match Rate ({date})",
                 "Match Rate (Matched Songs / Chart Size)", out3, ylim01=True)

if __name__ == "__main__":
    main()