# Stock Alert Bot (GitHub Actions + Telegram)

Get a Telegram notification when any of your stocks move by a chosen percentage (up or down).
Default threshold is **±10%**.

## Quick Start

1) **Create Telegram Bot**
   - In Telegram, search **@BotFather** → `/newbot` → follow prompts.
   - Copy the **HTTP API Token** → save for next step.

2) **Get Your Chat ID**
   - Send a message to your new bot first (e.g., "hi").
   - Then open in a browser:
     `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Find your `chat.id` in the JSON (e.g., `123456789`).

3) **GitHub Repo Setup**
   - Create a new repo and add this project.
   - Go to **Settings → Secrets and variables → Actions**:
     - **Secrets**:
       - `TELEGRAM_BOT_TOKEN` = *your bot token from BotFather*
       - `TELEGRAM_CHAT_ID`   = *the numeric chat id from getUpdates*
     - **Variables**:
       - `SYMBOLS`        = e.g., `AAPL,TSLA,MSFT`
       - `THRESHOLD_PCT`  = `10` (default)
       - `MODE`           = `daily` or `intraday`
       - `DIRECTION`      = `both` | `up` | `down`

4) **Run it**
   - Actions → select **Stock Alerts** → **Run workflow** (manual).
   - It will also run on the schedule (see workflow `.yml`).

## What it checks

- **daily** mode: compares latest daily close vs previous daily close.
- **intraday** mode: compares the most recent intraday price vs **yesterday’s close**.

If the change is ≥ `THRESHOLD_PCT` (positive or negative, depending on `DIRECTION`), it sends a Telegram message like:

