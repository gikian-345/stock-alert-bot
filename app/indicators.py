from __future__ import annotations
import pandas as pd
import yfinance as yf

def _pct_change_daily(symbol: str) -> float | None:
    """
    Daily change vs previous close, using 2 most recent daily closes.
    Returns percentage change (e.g., +12.3 means +12.3%).
    """
    try:
        df = yf.download(symbol, period="5d", interval="1d", auto_adjust=True, progress=False)
        # Need at least 2 rows to compare yesterday close vs latest close
        if df is None or df.empty or len(df) < 2:
            return None
        prev_close = float(df["Close"].iloc[-2])
        last_close = float(df["Close"].iloc[-1])
        if prev_close == 0:
            return None
        return (last_close - prev_close) / prev_close * 100.0
    except Exception:
        return None

def _pct_change_intraday(symbol: str) -> float | None:
    """
    Intraday change (current/last price vs previous close).
    Uses 1m data today where available; falls back to fast_info.
    """
    try:
        # Try intraday 1m snapshot
        df = yf.download(symbol, period="2d", interval="1m", auto_adjust=True, progress=False)
        if df is None or df.empty:
            return None

        # Get today's slice
        last_ts = df.index[-1]
        today = last_ts.date()
        today_df = df[df.index.date == today]
        if today_df.empty:
            # Market may be closed; fallback to daily
            return _pct_change_daily(symbol)

        last_price = float(today_df["Close"].iloc[-1])

        # Pull previous close from the previous day's last bar
        yday_df = df[df.index.date < today]
        if yday_df.empty:
            return None
        prev_close = float(yday_df["Close"].iloc[-1])
        if prev_close == 0:
            return None

        return (last_price - prev_close) / prev_close * 100.0
    except Exception:
        # Fallback: daily
        try:
            return _pct_change_daily(symbol)
        except Exception:
            return None

def percent_change(symbol: str, mode: str = "daily") -> float | None:
    mode = (mode or "daily").lower()
    if mode == "intraday":
        return _pct_change_intraday(symbol)
    return _pct_change_daily(symbol)
