import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# Carpeta donde guardar los CSVs
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

TICKERS = {
    "BTC": {"ticker": "BTC-USD", "filename": "btc.csv"},
    "SP500": {"ticker": "^GSPC", "filename": "sp500.csv"},
    "GOLD": {"ticker": "GC=F", "filename": "gold.csv"},
    "OIL": {"ticker": "CL=F", "filename": "oil.csv"},
    "US100": {"ticker": "^NDX", "filename": "us100.csv"},
    "SILVER": {"ticker": "SI=F", "filename": "silver.csv"},
    "COPPER": {"ticker": "HG=F", "filename": "copper.csv"},
    "NATGAS": {"ticker": "NG=F", "filename": "natgas.csv"},
}


def download_and_save_all(start="2010-01-01", end="2025-11-14"):
    for name, meta in TICKERS.items():
        df = yf.download(meta["ticker"], start=start, end=end, progress=False)
        if df.empty:
            print(f"[WARN] No se pudo descargar: {name}")
            continue
        path = os.path.join("data", meta["filename"])
        df.to_csv(path)
        print(f"[OK] {name} guardado en {path}")


def build_relative_price(asset_path, btc_path, output_path):
    asset = pd.read_csv(asset_path, index_col=0, parse_dates=True)
    btc = pd.read_csv(btc_path, index_col=0, parse_dates=True)

    # Asegurar columnas numéricas
    asset["Close"] = pd.to_numeric(asset["Close"], errors="coerce")
    btc["Close"] = pd.to_numeric(btc["Close"], errors="coerce")

    merged = asset[["Close"]].join(
        btc[["Close"]].rename(columns={"Close": "BTC_Close"}),
        how="inner"
    )

    # También forzar conversión por si acaso
    merged["Close"] = pd.to_numeric(merged["Close"], errors="coerce")
    merged["BTC_Close"] = pd.to_numeric(merged["BTC_Close"], errors="coerce")

    merged.dropna(inplace=True)  # Elimina filas con datos faltantes

    merged["Price_in_BTC"] = merged["Close"] / merged["BTC_Close"]
    merged = merged[["Price_in_BTC"]]

    merged.to_csv(output_path)
    print(f"[OK] Relativo guardado en {output_path}")



def plot_relative(csv_path, label):
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    plt.plot(df.index, df["Price_in_BTC"], label=label)


def main():
    print("=== DESCARGANDO DATOS ===")
    download_and_save_all()

    print("\n=== CONVIRTIENDO A BTC ===")
    btc_path = os.path.join("data", TICKERS["BTC"]["filename"])

    for name, meta in TICKERS.items():
        if name == "BTC":
            continue  # no convertimos BTC a BTC
        asset_path = os.path.join("data", meta["filename"])
        output_path = os.path.join("data_btc", f"{name.lower()}_btc.csv")
        try:
            build_relative_price(asset_path, btc_path, output_path)
        except Exception as e:
            print(f"[ERROR] {name} → {e}")

    print("\n=== GRAFICANDO ===")
    for name in ["SP500", "GOLD"]:  # aquí eliges los que quieres visualizar
        csv_path = os.path.join("data_btc", f"{name.lower()}_btc.csv")
        label = f"{name} en BTC"
        plot_relative(csv_path, label)

    plt.title("Activos expresados en BTC")
    plt.xlabel("Fecha")
    plt.ylabel("Valor relativo (BTC)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
