"""Application configuration loaded from environment variables (.env)."""

import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0") or "0")
VIP_CHANNEL_ID = int(os.getenv("VIP_CHANNEL_ID", "0") or "0")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///onward_signals.db")

TRC20_WALLET = os.getenv("TRC20_WALLET", "")
BSC_WALLET = os.getenv("BSC_WALLET", "")
BINANCE_UID = os.getenv("BINANCE_UID", "")

BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY", "")
TRONGRID_API_KEY = os.getenv("TRONGRID_API_KEY", "")

PRICE_MONTHLY = float(os.getenv("PRICE_MONTHLY", "49"))
PRICE_QUARTERLY = float(os.getenv("PRICE_QUARTERLY", "120"))
PRICE_YEARLY = float(os.getenv("PRICE_YEARLY", "399"))

TRIAL_DAYS = int(os.getenv("TRIAL_DAYS", "7"))
PAYMENT_AMOUNT_TOLERANCE = float(os.getenv("PAYMENT_AMOUNT_TOLERANCE", "0.5"))

PLAN_PRICES = {
    "monthly": PRICE_MONTHLY,
    "quarterly": PRICE_QUARTERLY,
    "yearly": PRICE_YEARLY,
}

PLAN_DURATIONS_DAYS = {
    "trial": TRIAL_DAYS,
    "monthly": 30,
    "quarterly": 90,
    "yearly": 365,
}

SCHEDULER_INTERVAL_SECONDS = int(os.getenv("SCHEDULER_INTERVAL_SECONDS", str(60 * 60)))

SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "oonyxa_Support3")

# Optional override for the tesseract binary path (rarely needed on Linux/Railway
# since nixpacks.toml installs tesseract-ocr into the system PATH).
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "")
