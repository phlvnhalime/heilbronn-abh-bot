# Heilbronn ABH appointment alert

A watcher that runs on your own computer. Every minute it opens the [Heilbronn immigration office appointment page](https://www.etermin.net/qtermin-stadtheilbronn-abh). When a new earlier time appears for **Verlängerung Aufenthaltserlaubnis**, it sends you a Telegram message.

It does not book the appointment, fill in a form, or send personal data. When the message arrives, you open the page and book the appointment yourself.

Someone else can do the same thing: copy this repository to their own GitHub account, create their own Telegram bot, and follow the steps below on their own computer.

## Before you start

- Python 3.11 or newer
- An internet connection
- A Telegram account
- A computer that can stay on. The check runs on that computer. If the computer sleeps or shuts down, it does not look. On a Mac the program tries to delay sleep; closing the lid can still put the machine to sleep.

## 1. Make your own copy

Open this repository on GitHub.

- If you see **Use this template**, click it. You can name the new repository `heilbronn-abh-bot`. GitHub creates a new repository on your account with these files.
- If that button is missing, use **Fork** to copy it to your account.

Then download your copy:

```bash
git clone https://github.com/YOUR_USERNAME/heilbronn-abh-bot.git
cd heilbronn-abh-bot
```

Replace `YOUR_USERNAME` with your GitHub username.

Making the repository a template is the owner's job: on GitHub, open the repository **Settings → General → Template repository**. When that box is checked, other people can use **Use this template** to start their own repository from the same files.

## 2. Create your Telegram bot

1. Open [@BotFather](https://t.me/BotFather) in Telegram.
2. Send `/newbot`.
3. Give the bot a display name. Example: `Heilbronn ABH`.
4. Give it a username. It must end in `bot`. Example: `heilbronn_abh_alert_bot`.
5. Copy the token BotFather gives you. That token is a password. Do not put it in a chat, a screenshot, or GitHub.

## 3. Get your chat id

1. Send your new bot a message. Example: `hello`.
2. Open this address in a browser. Replace `TOKEN` with your token:

```text
https://api.telegram.org/botTOKEN/getUpdates
```

3. In the text that appears, copy the number next to `"chat":{"id":`. That number is your `TELEGRAM_CHAT_ID`.
4. If the page shows an empty list (`"result":[]`), message the bot again and reload the address.
5. That page address contains your token. Do not share the link.

## 4. Install it on your computer

In the project folder:

```bash
bash setup.sh
```

That command:

- creates a Python environment named `.venv`
- installs the packages in `requirements.txt`
- downloads Chromium, which the program uses to read the page
- creates `.env` from `.env.example` when `.env` does not exist yet

On Windows, run the same steps by hand:

```bat
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
copy .env.example .env
```

## 5. Add your Telegram details

Open `.env` and fill in the two lines:

```text
TELEGRAM_BOT_TOKEN=the_token_from_BotFather
TELEGRAM_CHAT_ID=the_number_from_getUpdates
```

Do not put spaces around the `=` sign. Do not add quotes. Do not commit `.env` to GitHub. `.gitignore` already leaves that file out.

## 6. Check that Telegram works

```bash
source .venv/bin/activate
python test_telegram.py
```

On Windows the activate command is `.venv\Scripts\activate`.

If Telegram receives `Heilbronn ABH bot is running.`, your details are correct. If it does not, check the token, the chat id, and that you have sent the bot at least one message.

## 7. Start the watcher

In the same folder, with the environment still active:

```bash
python monitor.py
```

The program then checks the page at second `:00` of every minute. Stop it with `Ctrl+C` in that window.

The first successful check does not send an appointment message. It saves the earliest time it sees as the starting point. A message is sent later only when a time appears that is earlier than that saved time and has not been seen before.

The record is stored in `appointment_state.json`. That file is not uploaded to GitHub. Each person creates their own starting point on their own computer.

## What the screen shows

```text
Check: 15.11.2026 15:10:00
Earliest visible time: 2027-05-12 08:50 (43 slots)
No new earlier appointment. No alert sent.
Next check: 15:11:00 (exact minute, 53 seconds).
```

- `Check` is the moment the check started. Successful checks stay locked to second `:00` of each minute.
- `Earliest visible time` is the earliest appointment found on the page. The number in parentheses is how many times were read on that check.
- `No alert sent` means there is no new time earlier than the saved earliest time.
- `Next check` is the clock time of the next check. The seconds beside it are the time left until that minute after the page has finished loading.

When an earlier time is found, the terminal prints `Telegram alert sent.` and your phone receives a message like this:

```text
🔔 Heilbronn ABH — earlier appointment
📅 10.05.2027
🕒 10:50
⏳ 178 days from now
Service: Verlängerung Aufenthaltserlaubnis
https://www.etermin.net/qtermin-stadtheilbronn-abh
```

## If something looks wrong

- `.env must contain TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID`: step 5 is missing.
- `test_telegram.py` fails and you never see `Telegram message sent.`: the token or chat id is wrong, or you never messaged the bot.
- The same date stays on screen for hours: the page has no earlier time. The program is still working.
- `Check did not finish within 75 seconds and was stopped`: that check got stuck and was stopped. The next minute tries again.
- If the computer slept, a check can be skipped. After it wakes, checking continues at the next exact minute.

## What stays private

`.env`, the Telegram token, and `appointment_state.json` stay on your computer. The repository contains the program, `requirements.txt`, `.env.example`, and these instructions.
