import streamlit as st
import matplotlib.pyplot as plt

from core_backtest import (
    load_data_from_csv,
    add_moving_averages,
    run_backtest
)

# ---------- PAGE CONFIG ----------

st.set_page_config(
    page_title="Moving Average Crossover Backtester",
    layout="wide"
)

st.title("📈 Moving Average Crossover Backtester")
st.write(
    "Backtest a simple **moving average crossover** strategy on "
    "**NIFTY 50** and **Bank Nifty** using historical data."
)

# ---------- SIDEBAR CONTROLS ----------

st.sidebar.header("⚙️ Settings")

index_choice = st.sidebar.selectbox(
    "Select Index",
    options=["NIFTY 50", "Bank Nifty"],
    index=0
)

data_path_map = {
    "NIFTY 50": "data/nifty.csv",
    "Bank Nifty": "data/banknifty.csv",
}

short_window = st.sidebar.slider(
    "Short MA window (days)",
    min_value=5,
    max_value=50,
    value=20,
    step=1
)

long_window = st.sidebar.slider(
    "Long MA window (days)",
    min_value=20,
    max_value=200,
    value=50,
    step=5
)

if long_window <= short_window:
    st.sidebar.warning("⚠️ Long MA should be greater than Short MA for a proper crossover strategy.")

initial_capital = st.sidebar.number_input(
    "Initial Capital (₹)",
    min_value=10000.0,
    max_value=1e7,
    value=100000.0,
    step=10000.0,
    format="%.2f"
)

cost_perc = st.sidebar.number_input(
    "Transaction cost per trade side (%)",
    min_value=0.0,
    max_value=1.0,
    value=0.10,      # 0.10% = 0.001
    step=0.05,
    format="%.2f"
) / 100.0

run_button = st.sidebar.button("Run Backtest 🚀")

# ---------- MAIN AREA ----------

if run_button:
    try:
        path = data_path_map[index_choice]
        df = load_data_from_csv(path)
        df = add_moving_averages(df, short_window=short_window, long_window=long_window)
        df_bt, metrics = run_backtest(df, initial_capital=initial_capital, cost_perc=cost_perc)

        st.success("Backtest completed ✅")

        # ----- METRICS -----
        st.subheader("📊 Key Metrics")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Return (Strategy)", f"{metrics['total_return_pct']:.2f} %")
        col2.metric("Buy & Hold Return", f"{metrics['buy_hold_return_pct']:.2f} %")
        col3.metric("CAGR", f"{metrics['cagr_pct']:.2f} %")
        col4.metric("Sharpe Ratio", f"{metrics['sharpe']:.2f}")

        col5, col6, col7 = st.columns(3)
        col5.metric("Max Drawdown", f"{metrics['max_drawdown_pct']:.2f} %")
        col6.metric("Number of Trades", f"{metrics['num_trades']}")
        col7.metric("Win Rate", f"{metrics['win_rate_pct']:.2f} %")

        st.write(
            f"Average profit per trade: **{metrics['avg_profit_per_trade_pct']:.2f}%** (after transaction costs)"
        )

        # ----- PRICE + MA + SIGNALS PLOT -----
        st.subheader("📈 Price with Moving Averages & Trade Signals")

        fig_price, ax_price = plt.subplots(figsize=(10, 4))
        ax_price.plot(df_bt.index, df_bt["Close"], label="Close")
        ax_price.plot(df_bt.index, df_bt["MA_short"], label=f"Short MA ({short_window})")
        ax_price.plot(df_bt.index, df_bt["MA_long"], label=f"Long MA ({long_window})")

        df_bt["position_change"] = df_bt["position"].diff().fillna(0)
        buys = df_bt[df_bt["position_change"] == 1]
        sells = df_bt[df_bt["position_change"] == -1]

        ax_price.scatter(buys.index, buys["Close"], marker="^", s=80, label="Buy", alpha=0.8)
        ax_price.scatter(sells.index, sells["Close"], marker="v", s=80, label="Sell", alpha=0.8)

        ax_price.set_ylabel("Price")
        ax_price.legend()
        ax_price.grid(True, alpha=0.3)

        st.pyplot(fig_price)

        # ----- EQUITY CURVE PLOT -----
        st.subheader("💰 Equity Curve (Strategy vs Buy & Hold)")

        fig_eq, ax_eq = plt.subplots(figsize=(10, 4))
        ax_eq.plot(df_bt.index, df_bt["strategy_equity"], label="Strategy Equity")
        ax_eq.plot(df_bt.index, df_bt["buy_hold_equity"], label="Buy & Hold Equity", linestyle="--")

        ax_eq.set_ylabel("Equity (₹)")
        ax_eq.legend()
        ax_eq.grid(True, alpha=0.3)

        st.pyplot(fig_eq)

        # ----- OPTIONAL RAW DATA -----
        with st.expander("See sample backtest data"):
            st.dataframe(df_bt.head(10))

    except FileNotFoundError:
        st.error(
            f"Data file not found for {index_choice}. "
            "Make sure banknifty.csv and nifty.csv are inside the data/ folder."
        )
    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Set your parameters on the left and click **Run Backtest 🚀** to start.")
