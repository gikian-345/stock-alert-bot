from __future__ import annotations
import sys
from datetime import datetime
from .utils import env
from .universe_builder import get_universe
from .indicators import percent_change
from .messenger import send_telegram

def format_change(pct: float | None) -> str:
    if pct is None:
        return "(no data)"
    sign = "▲" if pct >= 0 else "▼"
    return f"{sign} {pct:.2f}%"

def run() -> int:
    symbols = get_universe()
    if not symbols:
        print("No symbols provided. Set SYMBOLS env var or commit tickers.txt.")
        return 0

    threshold = float(env("THRESHOLD_PCT", "10"))
    mode = (env("MODE", "daily") or "daily").lower()           # "daily" | "intraday"
    direction = (env("DIRECTION", "both") or "both").lower()   # "up" | "down" | "both"
    always_notify = (env("ALWAYS_NOTIFY", "0") or "0").lower() in ("1","true","yes")
    debug = (env("DEBUG", "1") or "1").lower() in ("1","true","yes")  # turned on by default

    hits = []
    snapshot = []

    print(f"[CONFIG] mode={mode}, threshold={threshold}, direction={direction}, always_notify={always_notify}")
    print(f"[CONFIG] symbols={symbols}")

    for sym in symbols:
        pct = percent_change(sym, mode=mode)
        snapshot.append((sym, pct))

        up_hit = (pct is not None) and (pct >= threshold)
        down_hit = (pct is not None) and (pct <= -threshold)
        notify = (
            (direction == "both" and (up_hit or down_hit))
            or (direction == "up" and up_hit)
            or (direction == "down" and down_hit)
        )
        if debug:
            print(f"[DEBUG] {sym} change={format_change(pct)} | up_hit={up_hit} down_hit={down_hit} notify={notify}")

        if notify and pct is not None:
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

    print("No alerts this run.")
    if always_notify:
        lines = [f"ℹ️ Stock Summary ({mode}, threshold {threshold:.0f}% not met): {now}"]
        for sym, pct in snapshot:
            lines.append(f"• {sym}: {format_change(pct)}")
        message = "\n".join(lines)
        send_telegram(message)
        print("Sent summary (ALWAYS_NOTIFY=1).")
    return 0

if __name__ == "__main__":
    sys.exit(run())
