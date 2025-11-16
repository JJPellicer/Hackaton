import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def simulate_gbm(series, days_ahead=1095, n_sims=500, seed=42):
    """
    Simula paths futuros usando Geometric Brownian Motion sobre una serie histórica.
    """
    np.random.seed(seed)

    log_returns = np.log(series / series.shift(1)).dropna()
    mu = log_returns.mean()
    sigma = log_returns.std()

    last_price = series.iloc[-1]
    last_date = series.index[-1]

    dt = 1
    drift = (mu - 0.5 * sigma ** 2) * dt
    shocks = sigma * np.random.randn(days_ahead, n_sims) * np.sqrt(dt)
    log_paths = np.cumsum(drift + shocks, axis=0)
    price_paths = last_price * np.exp(log_paths)

    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days_ahead, freq='D')
    df_sim = pd.DataFrame(price_paths, index=future_dates)

    df_out = pd.DataFrame({
        "future_median": df_sim.median(axis=1),
        "future_p25": df_sim.quantile(0.25, axis=1),
        "future_p75": df_sim.quantile(0.75, axis=1)
    })
    df_out.index.name = "Date"
    return df_out

def generate_future_projection(asset_name, input_path, output_dir="data_future", plot=False):
    """
    Carga un CSV histórico y genera proyección futura en BTC usando GBM.
    """
    df = pd.read_csv(input_path, index_col=0, parse_dates=True)

    if "Price_in_BTC" not in df.columns:
        raise ValueError(f"[{asset_name}] Falta la columna 'price_in_btc' en {input_path}")

    series = df["Price_in_BTC"].dropna()

    df_future = simulate_gbm(series)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{asset_name}_future.csv")
    df_future.to_csv(output_path)
    print(f"[OK] {asset_name} → futuro guardado en {output_path}")

    if plot:
        _plot_future(asset_name, series, df_future)

def _plot_future(asset_name, historical_series, future_df):
    """
    Muestra gráfica con histórico + mediana futura + intervalo p25–p75.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(historical_series.index, historical_series, label="Histórico", color="purple")
    plt.plot(future_df.index, future_df["future_median"], "--", label="Futuro (mediana)", color="gray")
    plt.fill_between(future_df.index, future_df["future_p25"], future_df["future_p75"],
                     color="gray", alpha=0.3, label="Futuro (p25–p75)")

    plt.axvline(x=historical_series.index[-1], color="black", linestyle=":", label="Corte pasado/futuro")
    plt.title(f"{asset_name.upper()} en BTC – Simulación Futura")
    plt.xlabel("Fecha")
    plt.ylabel("price_in_btc")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_future_only(asset_name, future_df):
    """
    Muestra solo la simulación futura (mediana y bandas p25-p75).
    """
    plt.figure(figsize=(14, 7))
    plt.plot(future_df.index, future_df["future_median"], label="Futuro (mediana)", color="black", linestyle="--", linewidth=2)
    plt.fill_between(future_df.index, future_df["future_p25"], future_df["future_p75"],
                     color="gray", alpha=0.4, label="Futuro (p25–p75)")
    plt.title(f"Proyección futura simulada – {asset_name.upper()} en BTC", fontsize=16)
    plt.xlabel("Fecha", fontsize=12)
    plt.ylabel("price_in_btc", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()



if __name__ == "__main__":
    # Solo usa los archivos que tú ya tienes y sabes que funcionan
    assets = {
    "gold": "data/gold_btc.csv",
    "sp500": "data/sp500_btc.csv",
    "oil": "data/oil_btc.csv",
    "us100": "data/us100_btc.csv",
    "cpi": "data/cpi_btc.csv",
    "silver": "data/silver_btc.csv",
    "copper": "data/copper_btc.csv",
    "natgas": "data/natgas_btc.csv"
}



    for asset, path in assets.items():
        generate_future_projection(asset, path, plot=True)  # Set plot=False to skip plotting
        future_path = f"data_future/{asset}_future.csv"
        df_future = pd.read_csv(future_path, index_col=0, parse_dates=True)
        plot_future_only(asset, df_future)