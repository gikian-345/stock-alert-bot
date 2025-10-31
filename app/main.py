from __future__ import annotations
import sys
from datetime import datetime
from .utils import env
from .universe_builder import get_universe
from .indicators import percent_change
from .messenger import send_telegram

def format_change(pct: float) -> str:
    sign = "▲" if pct >= 0 else "▼"
    return f"{sign} {pct:.2f}%"

def run() -> int:
    symbols = get_universe()
    if not symbols:
        print("No symbols provided. Set SYMBOLS env var or commit tickers.txt.")
        return 0

    # Config
    threshold = float(env("THRESHOLD_PCT", "10"))  # e.g., "10"
    mode = (env("MODE", "daily") or "daily").lower()  # "daily" or "intraday"
    direction = (env("DIRECTION", "both") or "both").lower()  # "up", "down", "both"

    hits = []
    for sym in symbols:
        pct = percent_change(sym, mode=mode)
        if pct is None:
            continue

        up_hit = pct >= threshold
        down_hit = pct <= -threshold

        notify = (
            (direction == "both" and (up_hit or down_hit))
            or (direction == "up" and up_hit)
            or (direction == "down" and down_hit)
        )
        if notify:
            hits.append((sym, pct))

    if not hits:
        print("No alerts this run.")
        return 0

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"📈 Stock Move Alert ({mode}, ≥{threshold:.0f}%): {now}"]
    for sym, pct in hits:
        lines.append(f"• {sym}: {format_change(pct)}")
    message = "\n".join(lines)

    send_telegram(message)
    print("Sent alert:\n", message)
    return 0

if __name__ == "__main__":
    sys.exit(run())
