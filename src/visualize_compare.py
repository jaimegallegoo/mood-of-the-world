import argparse
import pandas as pd
import matplotlib.pyplot as plt

def load_tagged(path: str, tag: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["tag"] = tag
    return df

def main():
    ap = argparse.ArgumentParser(description="Compare two processed CSVs (e.g., summer vs winter).")
    ap.add_argument("--a", required=True, help="CSV A (processed, with mood_index)")
    ap.add_argument("--b", required=True, help="CSV B (processed, with mood_index)")
    ap.add_argument("--outdir", default="figures", help="Output directory")
    args = ap.parse_args()

    a = load_tagged(args.a, "A")
    b = load_tagged(args.b, "B")
    df = pd.concat([a, b], ignore_index=True)

    # 1) Boxplot MoodIndex por tag
    plt.figure(figsize=(6,5))
    df.boxplot(column="mood_index", by="tag")
    plt.title("Mood Index: comparación A vs B")
    plt.suptitle("")
    plt.xlabel("Conjunto")
    plt.ylabel("Mood Index (valence+energy)/2")
    plt.tight_layout()
    plt.savefig(f"{args.outdir}/compare_boxplot.png", dpi=300)
    plt.close()

    # 2) Barras: medias (simple y ponderada)
    for col, name in [("track_popularity","ponderada"), (None,"simple")]:
        plt.figure(figsize=(6,4))
        if col and col in df.columns:
            g = df.groupby("tag").apply(lambda x: (x["mood_index"]*(x[col].clip(0,100)/100.0)).sum() / (x[col].clip(0,100)/100.0).sum())
        else:
            g = df.groupby("tag")["mood_index"].mean()
        g.plot(kind="bar")
        plt.title(f"Media {name} de Mood Index")
        plt.ylabel("Mood Index")
        plt.tight_layout()
        plt.savefig(f"{args.outdir}/compare_mean_{name}.png", dpi=300)
        plt.close()

    # 3) Scatter valence vs energy (ambos conjuntos)
    plt.figure(figsize=(6,5))
    for tag, sub in df.groupby("tag"):
        plt.scatter(sub["valence"], sub["energy"], label=tag, alpha=0.8, edgecolors="k")
    plt.xlabel("Valence")
    plt.ylabel("Energy")
    plt.title("Valence vs Energy (A vs B)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{args.outdir}/compare_scatter.png", dpi=300)
    plt.close()

    print("✅ Saved: compare_boxplot.png, compare_mean_simple.png, compare_mean_ponderada.png, compare_scatter.png")

if __name__ == "__main__":
    main()
