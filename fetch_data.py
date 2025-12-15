import yfinance as yf
import os

def download_index(ticker, filename, period="max"):
    os.makedirs("data", exist_ok=True)
    df = yf.download(ticker, period=period)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.to_csv(os.path.join("data", filename))
    print(f"Saved {filename} with {len(df)} rows")

if __name__ == "__main__":
    # NIFTY 50 & Bank Nifty tickers on Yahoo
    download_index("^NSEI", "nifty.csv")         # NIFTY 50
    download_index("^NSEBANK", "banknifty.csv")  # Bank Nifty
