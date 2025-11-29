import subprocess
from pathlib import Path
import sys

# === Configuración de Países y Fechas ===
# Estrategia para el paper:
# 1. Europa (ES, FR, DE, GB) vs América (US, BR) vs Asia/Oceanía (JP, AU)
# 2. Hemisferio Norte (Verano en Ago) vs Sur (Invierno en Ago: BR, AU)
TASKS = [
    # --- Europa ---
    {"cc": "ES", "country": "Spain", "date": "2017-08-01", "top": 50},
    {"cc": "ES", "country": "Spain", "date": "2018-01-05", "top": 50},
    {"cc": "FR", "country": "France", "date": "2017-08-01", "top": 50},
    {"cc": "FR", "country": "France", "date": "2018-01-05", "top": 50},
    {"cc": "DE", "country": "Germany", "date": "2017-08-01", "top": 50},
    {"cc": "DE", "country": "Germany", "date": "2018-01-05", "top": 50},
    {"cc": "GB", "country": "United Kingdom", "date": "2017-08-01", "top": 50},
    {"cc": "GB", "country": "United Kingdom", "date": "2018-01-05", "top": 50},

    # --- América ---
    {"cc": "US", "country": "United States", "date": "2017-08-01", "top": 50},
    {"cc": "US", "country": "United States", "date": "2018-01-05", "top": 50},
    {"cc": "BR", "country": "Brazil", "date": "2017-08-01", "top": 50}, # Invierno allí
    {"cc": "BR", "country": "Brazil", "date": "2018-01-05", "top": 50}, # Verano allí

    # --- Asia / Oceanía ---
    {"cc": "JP", "country": "Japan", "date": "2017-08-01", "top": 50},
    {"cc": "JP", "country": "Japan", "date": "2018-01-05", "top": 50},
    {"cc": "AU", "country": "Australia", "date": "2017-08-01", "top": 50}, # Invierno allí
    {"cc": "AU", "country": "Australia", "date": "2018-01-05", "top": 50}, # Verano allí
]

# Rutas de datos
CHARTS_PATH = "data/raw/worldwide_daily_song_ranking.csv"
# Asegúrate de haber ejecutado load_public_data.py previamente
FEATURES_CLEAN = "data/interim/audio_features_clean.csv"

# Usar el ejecutable de Python actual
PY = sys.executable

def run(cmd):
    print(">>", " ".join(cmd))
    subprocess.run(cmd, check=True)

def main():
    # Crear directorios necesarios
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/interim").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    
    # Verificar requisitos previos
    if not Path(CHARTS_PATH).exists():
        print(f"❌ Error: No se encuentra {CHARTS_PATH}")
        print("   Descarga el dataset de Kaggle y guárdalo ahí.")
        return

    if not Path(FEATURES_CLEAN).exists():
        print(f"⚠️ Aviso: No se encuentra {FEATURES_CLEAN}")
        print("   Ejecutando carga de datos públicos primero...")
        # Intentar buscar el raw original para generarlo
        raw_feats = "data/raw/SpotifyAudioFeaturesApril2019.csv"
        if Path(raw_feats).exists():
            run([PY, "src/load_public_data.py", "--input", raw_feats, "--out", FEATURES_CLEAN])
        else:
            print(f"❌ Error: Falta {raw_feats}. No se puede generar el dataset limpio.")
            return

    print(f"🚀 Iniciando procesamiento para {len(TASKS)} tareas...")

    for t in TASKS:
        cc = t["cc"]; cn = t["country"]; date = t["date"]; top = str(t["top"])

        sample_csv = f"data/raw/{cc}_sample_{date}.csv"
        meta_csv   = f"data/interim/{cc}_metadata_{date}.csv"
        out_csv    = f"data/processed/{cc}_mood_{date}.csv"

        print(f"\n--- Procesando: {cn} ({date}) ---")

        # 1) Select Top-N from charts
        # Si el fichero ya existe, podríamos saltarlo, pero mejor regenerar para asegurar consistencia
        run([PY, "src/select_from_charts.py",
             "--input", CHARTS_PATH,
             "--country", cc,
             "--date", date,
             "--top", top,
             "--out", sample_csv])

        # 2) Enrich via API (Metadata)
        # Este es el paso lento (rate limits).
        run([PY, "src/fetch_metadata.py",
             "--chart", sample_csv,
             "--country", cn,
             "--date", date,
             "--out", meta_csv])

        # 3) Merge + MoodIndex
        run([PY, "src/process_data.py",
             "--meta", meta_csv,
             "--features", FEATURES_CLEAN,
             "--out", out_csv])

    print("\n✅ Ejecución multi-país completada.")
    print("   Ahora ejecuta: python src/summarize.py para actualizar el resumen global.")

if __name__ == "__main__":
    main()