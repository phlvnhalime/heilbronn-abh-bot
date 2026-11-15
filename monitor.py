import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

INTERVAL_SECONDS = 15 * 60
CHECK_TIMEOUT_SECONDS = 75
TIMEZONE = ZoneInfo("Europe/Berlin")
ROOT = Path(__file__).resolve().parent


def next_mark(moment: datetime) -> datetime:
    """Next 15-minute mark in Berlin (:00, :15, :30, or :45). A moment already on the mark waits one full interval."""
    stamp = moment.timestamp()
    nxt = (int(stamp) // INTERVAL_SECONDS + 1) * INTERVAL_SECONDS
    return datetime.fromtimestamp(nxt, TIMEZONE)


def keep_awake() -> None:
    try:
        subprocess.Popen(
            ["caffeinate", "-ims", "-w", str(os.getpid())],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as exc:
        print(f"Could not prevent computer sleep: {exc}", flush=True)


def _stop(proc: subprocess.Popen) -> None:
    if proc.poll() is not None or not proc.pid:
        return
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)


def run_check() -> str:
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    proc = subprocess.Popen(
        [sys.executable, "-m", "appointment_checker"],
        cwd=ROOT,
        env=env,
        start_new_session=True,
    )
    try:
        code = proc.wait(timeout=CHECK_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        _stop(proc)
        return "timeout"
    except BaseException:
        _stop(proc)
        raise
    if code != 0:
        return f"exit {code}"
    return "ok"


def sleep_until(deadline: datetime) -> float:
    while True:
        remaining = (deadline - datetime.now(TIMEZONE)).total_seconds()
        if remaining <= 0.05:
            while datetime.now(TIMEZONE) < deadline:
                pass
            return max(0.0, (datetime.now(TIMEZONE) - deadline).total_seconds())
        time.sleep(min(remaining - 0.05, 1))


def require_telegram_env() -> None:
    load_dotenv(ROOT / ".env")
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise SystemExit(
            ".env must contain TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID. "
            "Copy .env.example to .env and add your own Telegram details."
        )


def run() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, OSError):
        pass
    require_telegram_env()
    keep_awake()
    print(
        "Heilbronn ABH monitor started. Checks run every 15 minutes, at :00, :15, :30, and :45. Press Ctrl+C to stop.",
        flush=True,
    )
    failures = 0
    while True:
        started = datetime.now(TIMEZONE)
        print(f"\nCheck: {started:%d.%m.%Y %H:%M:%S}", flush=True)
        status = run_check()
        if status == "ok":
            failures = 0
        else:
            failures += 1
            if status == "timeout":
                print(
                    f"Check did not finish within {CHECK_TIMEOUT_SECONDS} seconds and was stopped.",
                    flush=True,
                )
            else:
                print(f"Check error: {status}", flush=True)

        now = datetime.now(TIMEZONE)
        if failures:
            backoff = min(300, INTERVAL_SECONDS * 2 ** min(failures - 1, 3))
            deadline = now + timedelta(seconds=backoff)
            reason = "waiting after an error"
        else:
            deadline = next_mark(now)
            reason = "every 15 minutes"
        delay = max(0.0, (deadline - datetime.now(TIMEZONE)).total_seconds())
        print(
            f"Next check: {deadline:%H:%M:%S} ({reason}, {delay:.0f} seconds).",
            flush=True,
        )
        late = sleep_until(deadline)
        if late > 2:
            print(
                f"Started {late:.0f} seconds late. The next successful check locks back to the 15-minute mark.",
                flush=True,
            )


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\nMonitor stopped.", flush=True)
