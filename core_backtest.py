import pandas as pd
import numpy as np


# ---------- 1. LOAD DATA ----------

def load_data_from_csv(path: str) -> pd.DataFrame:
    """
    Loads price data and returns a DataFrame with Date index.
    Handles two formats:
      1) Normal:  Date,Open,High,Low,Close,Volume
      2) Your file: Price,Open,High,Low,Close,Volume + Ticker/^NSEI junk
    """
    df = pd.read_csv(path)

    # --- Handle your "Price, Ticker, ^NSEI" format ---
    if "Date" not in df.columns and "Price" in df.columns:
        # 'Price' column actually contains dates + some junk rows
        # Try to parse it as dates; invalid ones become NaT
        df["Date_parsed"] = pd.to_datetime(df["Price"], errors="coerce")
        # keep only rows where parsing succeeded (these are real dates)
        df = df.dropna(subset=["Date_parsed"])
        df["Date"] = df["Date_parsed"]
        df = df.drop(columns=["Date_parsed"])
    # -------------------------------------------------

    # Ensure we have a Date index
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df = df.sort_values("Date")
        df = df.set_index("Date")
    else:
        # Fallback: assume index is date-like
        df.index = pd.to_datetime(df.index, errors="coerce")
        df = df.sort_index()

    # Keep and clean numeric columns
    price_cols = ["Open", "High", "Low", "Close", "Volume"]
    df = df[price_cols]

    for col in price_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with invalid Close
    df = df.dropna(subset=["Close"])

    return df


# ---------- 2. INDICATORS & SIGNALS ----------

def add_moving_averages(
    df: pd.DataFrame,
    short_window: int = 20,
    long_window: int = 50
) -> pd.DataFrame:
    """
    Add short and long moving averages and a position column:
    position = 1 when MA_short > MA_long, else 0.
    """
    df = df.copy()

    df["MA_short"] = df["Close"].rolling(window=short_window, min_periods=1).mean()
    df["MA_long"] = df["Close"].rolling(window=long_window, min_periods=1).mean()

    # Today's signal
    df["signal"] = 0
    df.loc[df["MA_short"] > df["MA_long"], "signal"] = 1

    # Trade using yesterday’s signal (avoid look-ahead bias)
    df["position"] = df["signal"].shift(1).fillna(0)

    return df


# ---------- 3. BACKTEST ENGINE ----------

def run_backtest(
    df: pd.DataFrame,
    initial_capital: float = 100000.0,
    cost_perc: float = 0.001
):
    """
    Run a long-only MA crossover backtest.

    cost_perc = transaction cost (like 0.001 = 0.1%) per trade side.
    """
    df = df.copy()

    # Underlying daily returns
    df["market_return"] = df["Close"].pct_change().fillna(0)

    # Strategy daily return = position * market_return
    df["strategy_return"] = df["position"] * df["market_return"]

    # Pay transaction cost whenever position changes (0->1 or 1->0)
    df["trade"] = df["position"].diff().abs().fillna(0)
    df.loc[df["trade"] > 0, "strategy_return"] -= cost_perc

    # Equity curves
    df["strategy_equity"] = (1 + df["strategy_return"]).cumprod() * initial_capital
    df["buy_hold_equity"] = (1 + df["market_return"]).cumprod() * initial_capital

    metrics = compute_all_metrics(df, initial_capital)
    return df, metrics


# ---------- 4. METRICS ----------

def compute_all_metrics(df: pd.DataFrame, initial_capital: float):
    metrics = {}

    final_equity = df["strategy_equity"].iloc[-1]
    final_bh = df["buy_hold_equity"].iloc[-1]

    metrics["total_return_pct"] = (final_equity / initial_capital - 1) * 100
    metrics["buy_hold_return_pct"] = (final_bh / initial_capital - 1) * 100

    # CAGR
    days = (df.index[-1] - df.index[0]).days
    years = days / 365.25 if days > 0 else 0
    if years > 0 and final_equity > 0:
        metrics["cagr_pct"] = (
            (final_equity / initial_capital) ** (1 / years) - 1
        ) * 100
    else:
        metrics["cagr_pct"] = 0.0

    # Sharpe
    daily_ret = df["strategy_return"]
    if daily_ret.std() > 0:
        sharpe = (daily_ret.mean() / daily_ret.std()) * np.sqrt(252)
    else:
        sharpe = 0.0
    metrics["sharpe"] = sharpe

    # Max drawdown
    roll_max = df["strategy_equity"].cummax()
    drawdown = df["strategy_equity"] / roll_max - 1.0
    metrics["max_drawdown_pct"] = drawdown.min() * 100  # negative value

    # Trade stats
    trade_stats = compute_trade_stats(df)
    metrics.update(trade_stats)

    return metrics


def compute_trade_stats(df: pd.DataFrame):
    """
    Compute number of trades, win rate, average profit per trade
    based on position changes.
    """
    stats = {}
    df = df.copy()

    df["position_change"] = df["position"].diff().fillna(0)

    entries = list(df.index[df["position_change"] == 1])   # 0 -> 1
    exits = list(df.index[df["position_change"] == -1])    # 1 -> 0

    # If ending still in position, close on last date
    if len(entries) > len(exits):
        exits.append(df.index[-1])

    trade_returns = []

    for entry, exit_ in zip(entries, exits):
        mask = (df.index > entry) & (df.index <= exit_)
        if mask.sum() == 0:
            continue
        r = (1 + df.loc[mask, "strategy_return"]).prod() - 1
        trade_returns.append(r)

    trade_returns = np.array(trade_returns)
    num_trades = len(trade_returns)
    stats["num_trades"] = int(num_trades)

    if num_trades == 0:
        stats["win_rate_pct"] = 0.0
        stats["avg_profit_per_trade_pct"] = 0.0
    else:
        stats["win_rate_pct"] = float((trade_returns > 0).mean() * 100)
        stats["avg_profit_per_trade_pct"] = float(trade_returns.mean() * 100)

    return stats


# ---------- 5. QUICK TEST ----------

if __name__ == "__main__":
    df = load_data_from_csv("data/nifty.csv")
    df = add_moving_averages(df, short_window=20, long_window=50)
    df_bt, metrics = run_backtest(df, initial_capital=100000, cost_perc=0.001)

    print("Backtest metrics on NIFTY:")
    for k, v in metrics.items():
        print(f"{k:25s}: {v:.2f}")

    print("\nFirst 5 rows with signals & equity:")
    print(df_bt[["Close", "MA_short", "MA_long", "position", "strategy_equity"]].head())
