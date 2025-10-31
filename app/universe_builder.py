from .utils import env, parse_symbols

def get_universe() -> list[str]:
    # Preferred: repository variable SYMBOLS, comma-separated (e.g., AAPL,TSLA,MSFT)
    raw = env("SYMBOLS", "")
    if raw:
        return parse_symbols(raw)

    # Fallback: tickers.txt checked into the repo (optional). Keep empty if not needed.
    try:
        with open("tickers.txt", "r", encoding="utf-8") as f:
            raw = f.read()
            return parse_symbols(raw)
    except FileNotFoundError:
        return []
