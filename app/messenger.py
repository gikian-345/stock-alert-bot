from __future__ import annotations
import requests
from .utils import env

def send_telegram(text: str) -> None:
    token = env("TELEGRAM_BOT_TOKEN", required=True)
    chat_id = env("TELEGRAM_CHAT_ID", required=True)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.get(url, params={"chat_id": chat_id, "text": text})
    try:
        data = resp.json()
    except Exception:
        data = {"ok": False, "description": f"Non-JSON response: {resp.text}"}

    if not data.get("ok", False):
        raise RuntimeError(f"Telegram error: {data}")

def test_ping() -> None:
    send_telegram("✅ Stock alert bot is connected and ready.")
