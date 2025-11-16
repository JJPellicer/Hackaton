import os
import pandas as pd

# Folder where your CSVs are stored
input_folder = "data_btc"
output_folder = "data_btc"

os.makedirs(output_folder, exist_ok=True)

# List of CSVs to fix
files = [
    "oil_btc.csv",
    "gold_btc.csv",
    "us100_btc.csv",
    "sp500_btc.csv",
    "silver_btc.csv",
    "copper_btc.csv",
    "natgas_btc.csv"
]


for filename in files:
    in_path = os.path.join(input_folder, filename)
    out_path = os.path.join(output_folder, filename)

    print(f"Processing {filename}...")

    df = pd.read_csv(in_path)

    # Rename "price" → "Date"
    if "Price" in df.columns:
        df = df.rename(columns={"Price": "Date"})

    # Ensure Date is parsed correctly
    df["Date"] = pd.to_datetime(df["Date"])

    # Save fixed CSV
    df.to_csv(out_path, index=False)

    print(f"Saved → {out_path}")

print("\n✓ All files processed successfully.")
