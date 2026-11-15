#!/usr/bin/env bash
# Local setup: virtual environment, packages, and Chromium. Telegram details are typed into .env by hand.
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 was not found. Install Python 3.11 or newer first."
  exit 1
fi

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo
  echo ".env was created. Fill in TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID."
  echo "Then run: source .venv/bin/activate && python test_telegram.py"
else
  echo
  echo ".env already exists. To test it: source .venv/bin/activate && python test_telegram.py"
fi
