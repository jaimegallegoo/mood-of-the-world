import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Generate seasonal comparison chart (English labels)")
    parser.add_argument("--summary", default="data/processed/country_summary.csv")
    parser.add_argument("--outdir", default="figures")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    
    # Load data
    df = pd.read_csv(args.summary)
    
    # Define labels for the legend based on date
    def get_season_label(date_str):
        if "08-01" in str(date_str):
            return "Aug '17 (Northern Summer)"
        elif "01-05" in str(date_str):
            return "Jan '18 (Northern Winter)"
        return date_str

    df["Season Label"] = df["date"].apply(get_season_label)
    
    # Configure style
    sns.set_theme(style="whitegrid")
    
    # Create grouped bar chart
    plt.figure(figsize=(12, 6))
    
    # Using w_mean_streams as the main metric
    chart = sns.barplot(
        data=df, 
        x="country", 
        y="w_mean_streams", 
        hue="Season Label",
        palette={"Aug '17 (Northern Summer)": "#FF8C00", "Jan '18 (Northern Winter)": "#1E90FF"}
    )
    
    plt.title("Seasonal Comparison of Music Mood Index", fontsize=15)
    plt.ylabel("Weighted Mood Index (0=Sad/Calm, 1=Happy/Energetic)", fontsize=11)
    plt.xlabel("Country", fontsize=11)
    plt.ylim(0.45, 0.75) # Optimized scale to highlight differences
    plt.legend(title="Time Period")
    
    # Save
    out_path = os.path.join(args.outdir, "seasonal_comparison.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    print(f"✅ Saved English seasonal chart: {out_path}")

if __name__ == "__main__":
    main()