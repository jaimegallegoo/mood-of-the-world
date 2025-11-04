# src/visualize_countries.py
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_bar(d: pd.DataFrame, col: str, title: str, ylabel: str, out_path: str, ylim01=False):
    plt.figure(figsize=(8,5))
    plt.bar(d["country"], d[col])
    plt.title(title)
    plt.ylabel(ylabel)
    if ylim01:
        plt.ylim(0, 1)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"✅ {out_path}")

def main():
    ap = argparse.ArgumentParser(description="Visualizaciones multi-país desde country_summary.csv")
    ap.add_argument("--summary", default="data/processed/country_summary.csv", help="Ruta al summary CSV")
    ap.add_argument("--outdir", default="figures", help="Directorio de salida para las figuras")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    df = pd.read_csv(args.summary)

    # sanity check de columnas
    needed = {"country","date","mean","w_mean_streams","match_rate"}
    if not needed.issubset(df.columns):
        raise SystemExit(f"Faltan columnas en {args.summary}. Se necesitan: {sorted(needed)}")

    for date in sorted(df["date"].unique()):
        d = df[df["date"] == date].copy()

        # 1) Media simple
        d1 = d.sort_values("mean", ascending=False)
        out1 = os.path.join(args.outdir, f"mood_by_country_mean_{date}.png")
        plot_bar(d1, "mean", f"MoodIndex medio por país ({date})",
                 "MoodIndex (valence+energy)/2", out1)

        # 2) Media ponderada por streams
        d2 = d.sort_values("w_mean_streams", ascending=False)
        out2 = os.path.join(args.outdir, f"mood_by_country_wstreams_{date}.png")
        plot_bar(d2, "w_mean_streams", f"MoodIndex ponderado por Streams ({date})",
                 "MoodIndex (ponderado por streams del chart)", out2)

        # 3) Match rate (cobertura)
        d3 = d.sort_values("match_rate", ascending=False)
        out3 = os.path.join(args.outdir, f"match_rate_{date}.png")
        plot_bar(d3, "match_rate", f"Match rate por país ({date})",
                 "n_matched / n_chart", out3, ylim01=True)

if __name__ == "__main__":
    main()
