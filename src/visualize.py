import argparse
import pandas as pd
import matplotlib.pyplot as plt


def plot_mood_index_bar(df: pd.DataFrame, out_path: str):
    """
    Create a bar chart of Mood Index per song.
    """
    df_sorted = df.sort_values("mood_index", ascending=False)

    plt.figure(figsize=(10, 6))
    plt.barh(df_sorted["track_name"], df_sorted["mood_index"], color="mediumseagreen")
    plt.xlabel("Mood Index (valence + energy)/2")
    plt.ylabel("Song")
    plt.title("Mood Index per Song")
    plt.gca().invert_yaxis()
    plt.tight_layout()

    plt.savefig(out_path)
    plt.close()
    print(f"💾 Saved bar chart to {out_path}")


def plot_valence_vs_energy(df: pd.DataFrame, out_path: str):
    """
    Create a scatter plot of valence vs energy to visualize song emotion space.
    """
    plt.figure(figsize=(7, 6))
    plt.scatter(df["valence"], df["energy"], s=100, c=df["mood_index"], cmap="coolwarm", edgecolors="k")

    for _, row in df.iterrows():
        plt.text(row["valence"] + 0.01, row["energy"], row["track_name"], fontsize=9)

    plt.xlabel("Valence (positivity/happiness)")
    plt.ylabel("Energy (intensity/activity)")
    plt.title("Valence vs Energy")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    plt.savefig(out_path)
    plt.close()
    print(f"💾 Saved scatter plot to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Visualize Mood Index results.")
    parser.add_argument("--input", required=True, help="Path to processed CSV file (from process_data.py)")
    parser.add_argument("--outdir", default="figures", help="Directory to save figures")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    if df.empty:
        print("⚠️ Empty dataset. Nothing to plot.")
        return

    bar_path = f"{args.outdir}/mood_index_bar.png"
    scatter_path = f"{args.outdir}/valence_vs_energy.png"

    plot_mood_index_bar(df, bar_path)
    plot_valence_vs_energy(df, scatter_path)
    print("✅ Visualization completed.")


if __name__ == "__main__":
    main()
