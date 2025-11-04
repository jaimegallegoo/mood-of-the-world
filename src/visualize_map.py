# src/visualize_map.py
import argparse, os, zipfile, io, re
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Diccionario para casar nombres de tu CSV con Natural Earth (columna ADMIN)
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

# CDN oficiales de Natural Earth (110m = baja resolución, suficiente para paper)
NE_URLS = [
    "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip",
    "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip",
]

def ensure_admin0_local(out_dir="data/external/ne_admin0") -> str:
    """
    Descarga y descomprime el shapefile de países si no existe.
    Devuelve la ruta a la carpeta que contiene los archivos .shp/.dbf/.shx/.prj.
    """
    os.makedirs(out_dir, exist_ok=True)
    # ¿ya descomprimido?
    shp_candidates = [f for f in os.listdir(out_dir) if f.endswith(".shp")]
    if shp_candidates:
        return out_dir

    # si no, intenta descargar y extraer
    for url in NE_URLS:
        try:
            print(f"🌐 Descargando Natural Earth (admin0): {url}")
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                # Extraer todos los archivos al directorio
                z.extractall(out_dir)
            # Comprobar que existe el .shp
            shp_candidates = [f for f in os.listdir(out_dir) if f.endswith(".shp")]
            if shp_candidates:
                print(f"✅ Shapefile listo en {out_dir}")
                return out_dir
        except Exception as e:
            print(f"⚠️  Fallo al descargar desde {url}: {e}")

    raise SystemExit("❌ No se pudo obtener el shapefile de países (Natural Earth).")

def main():
    ap = argparse.ArgumentParser(description="Mapa mundial del MoodIndex por país")
    ap.add_argument("--summary", default="data/processed/country_summary.csv", help="CSV con resumen por país/fecha")
    ap.add_argument("--date", required=True, help="Fecha a mapear (YYYY-MM-DD)")
    ap.add_argument("--metric", default="mean", choices=["mean", "w_mean_streams"], help="Métrica a pintar")
    ap.add_argument("--outdir", default="figures", help="Carpeta de salida")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # 1) Cargar resumen y filtrar por fecha
    df = pd.read_csv(args.summary)
    df = df[df["date"] == args.date].copy()
    if df.empty:
        raise SystemExit(f"No hay filas para la fecha {args.date} en {args.summary}")

    # Normalizar nombres para casarlos con Natural Earth (columna ADMIN)
    df["country_plot"] = df["country"].map(lambda x: NAME_FIX.get(x, x))

    # 2) Asegurar shapefile local y leerlo
    admin0_dir = ensure_admin0_local()
    # Busca el .shp dentro del directorio
    shp_files = [os.path.join(admin0_dir, f) for f in os.listdir(admin0_dir) if f.endswith(".shp")]
    if not shp_files:
        raise SystemExit("❌ No se encontró ningún .shp tras la descarga.")
    world = gpd.read_file(shp_files[0])  # contiene columnas como ADMIN, NAME, geometry

    # 3) Merge por nombre de país
    merged = world.merge(df, left_on="ADMIN", right_on="country_plot", how="left")

    # 4) Pintar
    metric = args.metric
    title = f"MoodIndex por país ({metric}) — {args.date}"

    plt.figure(figsize=(12, 6))
    ax = merged.plot(
        column=metric,
        cmap="viridis",
        legend=True,
        missing_kwds={"color": "lightgrey", "edgecolor": "white", "hatch": "///", "label": "Sin datos"},
    )
    ax.set_title(title)
    ax.set_axis_off()

    # Asegura que aparezca "Sin datos" en la leyenda
    handles, labels = ax.get_legend_handles_labels()
    if "Sin datos" not in labels:
        from matplotlib.patches import Patch
        handles.append(Patch(facecolor="lightgrey", edgecolor="white", hatch="///", label="Sin datos"))
        labels.append("Sin datos")
        ax.legend(handles=handles, labels=labels, loc="lower left")

    out = os.path.join(args.outdir, f"map_{metric}_{args.date}.png")
    plt.tight_layout()
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"✅ {out}")

if __name__ == "__main__":
    main()
