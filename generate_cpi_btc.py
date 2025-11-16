import os
import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import StringIO

ROOT = os.path.dirname(os.path.abspath(__file__))

btc_path = os.path.join(ROOT, "data", "btc.csv")
output_path = os.path.join(ROOT, "data", "cpi_btc.csv")

# ======================
# LOAD CPI
# ======================
def download_cpi_from_fred():
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"
    r = requests.get(url)

    df = pd.read_csv(StringIO(r.text), encoding="utf-8-sig")

    df = df.rename(columns={
        "observation_date": "Date",
        "CPIAUCSL": "CPI_USD"
    })

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["CPI_USD"] = pd.to_numeric(df["CPI_USD"], errors="coerce")

    df = df.dropna(subset=["Date", "CPI_USD"])

    print("[DEBUG] CPI loaded:", df.head())
    return df[["Date", "CPI_USD"]]


# ======================
# LOAD BTC
# ======================
def load_btc(path):
    df = pd.read_csv(path, encoding="utf-8-sig")

    # FIX hidden BOM or weird column names
    cols = list(df.columns)
    if cols[0].startswith("\ufeff"):
        df = df.rename(columns={cols[0]: "Date"})
    else:
        df = df.rename(columns={cols[0]: "Date"})

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Force numeric conversion
    if "BTC_USD" not in df.columns:
        df = df.rename(columns={"Close": "BTC_USD"})

    df["BTC_USD"] = pd.to_numeric(df["BTC_USD"], errors="coerce")

    df = df.dropna(subset=["Date", "BTC_USD"])

    print("[DEBUG] BTC loaded:", df.head())
    return df[["Date", "BTC_USD"]]


# ======================
# MERGE + COMPUTE
# ======================
def compute_cpi_in_btc(cpi, btc):
    cpi["Date"] = pd.to_datetime(cpi["Date"])
    btc["Date"] = pd.to_datetime(btc["Date"])

    merged = pd.merge(cpi, btc, on="Date", how="inner")

    print("[DEBUG] merged dtypes:")
    print(merged.dtypes)

    merged["Price_in_BTC"] = merged["CPI_USD"] / merged["BTC_USD"]

    return merged[["Date", "Price_in_BTC"]]


# ======================
# PLOT
# ======================
def plot(df):
    plt.figure(figsize=(12,5))
    plt.plot(df["Date"], df["Price_in_BTC"], color="purple")
    plt.title("CPI in BTC")
    plt.grid(True)
    plt.show()


# ======================
# MAIN
# ======================
if __name__ == "__main__":
    print(">> Generando CPI expresada en BTC...")

    cpi = download_cpi_from_fred()
    btc = load_btc(btc_path)

    final = compute_cpi_in_btc(cpi, btc)
    final.to_csv(output_path, index=False)

    print(f"[OK] Guardado en {output_path}")
    plot(final)
