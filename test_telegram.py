import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()


def send_telegram_message(message):
    if not TOKEN or not CHAT_ID:
        raise SystemExit(
            ".env must contain TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID. "
            "Copy .env.example to .env and fill it in."
        )
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": CHAT_ID, "text": message},
        timeout=15,
    )
    response.raise_for_status()
    if not response.json().get("ok"):
        raise RuntimeError("Telegram did not accept the message")
    print("Telegram message sent.")


if __name__ == "__main__":
    try:
        send_telegram_message(
            "Heilbronn ABH bot is running.\n\n"
            "Service: Verlängerung Aufenthaltserlaubnis\n"
            "Next step: python monitor.py"
        )
    except requests.RequestException as exc:
        print(f"Could not reach Telegram: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
