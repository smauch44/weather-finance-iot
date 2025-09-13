# finance_now.py
import os
from pathlib import Path
from dotenv import load_dotenv
import yfinance as yf

# Load .env (optional: YF_TICKER)
load_dotenv(Path(__file__).resolve().parent / ".env")

def get_quote(symbol: str | None = None):
    """
    Return a compact dict with current quote using yfinance.
    If symbol is None, use YF_TICKER from .env (default MSFT).
    """
    if not symbol:
        symbol = (os.getenv("YF_TICKER") or "MSFT").strip().upper()

    t = yf.Ticker(symbol)
    fi = t.fast_info  # lightweight snapshot

    # fi fields can be None depending on symbol/market; guard & cast safely
    price = fi.last_price
    ccy = fi.currency or "USD"
    exch = fi.exchange or "N/A"

    if price is None:
        # Fallback: try 'info' (heavier). Still rare to need this.
        info = t.info or {}
        price = info.get("regularMarketPrice")
        ccy = info.get("currency", ccy)
        exch = info.get("fullExchangeName", exch)

    if price is None:
        raise RuntimeError(f"Could not fetch a price for {symbol} (rate limited or unavailable).")

    return {
        "source": "yahoo-finance",
        "symbol": symbol,
        "price": float(price),
        "currency": ccy,
        "exchange": exch,
    }

if __name__ == "__main__":
    print(get_quote())
