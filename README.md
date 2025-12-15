# Moving Average Crossover Backtester
This project is a simple but realistic trading strategy backtester built in Python.<br>
I created it to understand how trading strategies actually perform over time, instead of just plotting indicators and assuming profits.<br>
The app tests a Moving Average Crossover strategy on NIFTY 50 and Bank Nifty, includes transaction costs, calculates real risk metrics, and visualizes everything through an interactive Streamlit UI.

## What this project does
- Uses historical market data
- Applies a 20-day vs 50-day moving average crossover strategy
- Simulates real trades with capital constraints
- Includes transaction costs
- Measures performance using professional metrics
- Compares results against Buy & Hold
- Shows everything in a clean web interface

## Strategy Logic
- Buy when the 20-day moving average crosses above the 50-day moving average
- Sell when the 20-day moving average crosses below the 50-day moving average
- Only one position at a time
- No leverage
- No future data leakage

## Results Snapshot (NIFTY 50)

The strategy slightly outperforms Buy & Hold while maintaining better risk control.

## Features
- Interactive Streamlit dashboard
- Adjustable parameters:
    - Short MA
    - Long MA
    - Initial capital
    - Transaction cost
- Visualizations:
    - Price chart with buy/sell signals
    - Strategy vs Buy & Hold equity curve
- Risk metrics:
    - CAGR
    - Sharpe ratio
    - Max drawdown
    - Win rate

## Tech Stack
- Python
- pandas / numpy –> data handling
- matplotlib –> charts
- Streamlit –> UI
- yfinance –> historical data

## Project Structure
```
MovingAverage/
│
├── app.py            # Streamlit user interface
├── core_backtest.py  # Strategy logic & backtesting engine
├── fetch_data.py     # Data downloader
├── data/
│   ├── nifty.csv
│   └── banknifty.csv
└── requirements.txt
```

## How to Run the Project
- 1. Clone the repository
    ```
    git clone https://github.com/Dhrub-Kumar-Garg/MovingAverage.git
    cd MovingAverage
    ```
- 2. Install dependencies
  ```
  pip install pandas
  pip install numpy
  pip install streamlit
  pip install matplotlib
  pip install yfinance
  ```
- 3. Run the app
  ```
  python -m streamlit run app.py
  ```
  Open in the browser
  ```
  http://localhost:8501
  ```

## About Me
Dhrub Kumar Garg<br>
Student of VIT Vellore
  
