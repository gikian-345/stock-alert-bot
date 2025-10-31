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

    threshold = float(env("THRESHOLD_PCT", "10"))
    mode = (env("MODE", "daily") or "daily").lower()  # "daily" or "intraday"
    direction = (env("DIRECTION", "both") or "both").lower()  # "up", "down", "both"
    always_notify = (env("ALWAYS_NOTIFY", "0") or "0") in ("1", "true", "True")

    hits = []
    snapshot = []  # collect all % changes for optional summary

    for sym in symbols:
        pct = percent_change(sym, mode=mode)
        if pct is None:
            snapshot.append((sym, None))
            continue

        snapshot.append((sym, pct))
        up_hit = pct >= threshold
        down_hit = pct <= -threshold

        notify = (
            (direction == "both" and (up_hit or down_hit))
            or (direction == "up" and up_hit)
            or (direction == "down" and down_hit)
        )
        if notify:
            hits.append((sym, pct))

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    if hits:
        lines = [f"📈 Stock Move Alert ({mode}, ≥{threshold:.0f}%): {now}"]
        for sym, pct in hits:
            lines.append(f"• {sym}: {format_change(pct)}")
        message = "\n".join(lines)
        send_telegram(message)
        print("Sent alert:\n", message)
        return 0

    # No alerts crossed threshold
    print("No alerts this run.")
    if always_notify:
        lines = [f"ℹ️ Stock Summary ({mode}, threshold {threshold:.0f}% not met): {now}"]
        for sym, pct in snapshot:
            if pct is None:
                lines.append(f"• {sym}: (no data)")
            else:
                lines.append(f"• {sym}: {format_change(pct)}")
        message = "\n".join(lines)
        send_telegram(message)
        print("Sent summary (ALWAYS_NOTIFY=1).")
    return 0

if __name__ == "__main__":
    sys.exit(run())
