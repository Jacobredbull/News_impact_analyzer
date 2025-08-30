# ticker_validator.py

import pandas as pd
import os

# URLs for official ticker lists
TICKER_URLS = {
    "NASDAQ": "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt",
    "NYSE": "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
}
CACHE_FILE = "all_tickers.txt"


def get_ticker_list() -> set:
    """
    Downloads and caches a comprehensive list of US stock tickers.
    Returns a set for fast lookups.
    """
    if os.path.exists(CACHE_FILE):
        print("Loading tickers from local cache...")
        with open(CACHE_FILE, 'r') as f:
            tickers = set(f.read().splitlines())
        return tickers

    print("Downloading official ticker lists...")
    all_tickers = set()
    for exchange, url in TICKER_URLS.items():
        try:
            # The files are pipe-delimited
            df = pd.read_csv(url, sep='|')
            # The ticker is in the 'Symbol' column for NASDAQ, 'ACT Symbol' for NYSE
            ticker_column = 'Symbol' if 'Symbol' in df.columns else 'ACT Symbol'

            # Remove the last row which is a file footer
            df = df[:-1]

            # Add valid tickers to our set
            all_tickers.update(df[ticker_column].dropna().tolist())
            print(f"-> Successfully processed {exchange} tickers.")
        except Exception as e:
            print(f"❗️ Could not download or parse tickers from {exchange}: {e}")

    # Cache the list for future runs
    with open(CACHE_FILE, 'w') as f:
        for ticker in sorted(list(all_tickers)):
            f.write(f"{ticker}\n")

    print(f"Cached {len(all_tickers)} tickers to {CACHE_FILE}.")
    return all_tickers


# --- Example of how to use it ---
if __name__ == "__main__":
    # This will run once to create the cache file
    tickers = get_ticker_list()
    print(f"Total unique tickers loaded: {len(tickers)}")
    # Test it
    print(f"Is 'AAPL' a valid ticker? {'AAPL' in tickers}")
    print(f"Is 'GROUP' a valid ticker? {'GROUP' in tickers}")