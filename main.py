"""Entry point: wires up handlers, the hourly expiry job, and starts polling."""

import logging
from datetime import time
from zoneinfo import ZoneInfo

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

import config
import database
from handlers.payment import admin_decision_callback, photo_handler
from handlers.plans import payment_method_callback, plan_callback
from handlers.start import language_callback, start_command, status_command
from handlers.trades import (
    group_message_handler,
    send_daily_report,
    stats_callback,
    stats_command,
    today_report_command,
)
from scheduler import check_expired_subscriptions

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_application() -> Application:
    if not config.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set. Check your .env file.")

    application = Application.builder().token(config.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CallbackQueryHandler(language_callback, pattern=r"^lang_"))
    application.add_handler(CallbackQueryHandler(plan_callback, pattern=r"^plan_"))
    application.add_handler(CallbackQueryHandler(payment_method_callback, pattern=r"^paymethod_"))
    application.add_handler(CallbackQueryHandler(admin_decision_callback, pattern=r"^admin_(approve|reject)_\d+$"))
    application.add_handler(CallbackQueryHandler(stats_callback, pattern=r"^show_stats$"))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("t", today_report_command))

    if config.TRADES_GROUP_ID:
        application.add_handler(
            MessageHandler(filters.TEXT & filters.Chat(chat_id=config.TRADES_GROUP_ID), group_message_handler)
        )

    application.job_queue.run_repeating(
        check_expired_subscriptions,
        interval=config.SCHEDULER_INTERVAL_SECONDS,
        first=10,
        name="check_expired_subscriptions",
    )

    if config.PUBLIC_CHANNEL_ID:
        application.job_queue.run_daily(
            send_daily_report,
            time=time(hour=0, minute=0, tzinfo=ZoneInfo(config.REPORT_TIMEZONE)),
            name="daily_trade_report",
        )

    return application


def main() -> None:
    database.init_db()
    application = build_application()
    logger.info("Oonyx Ai Bot starting...")
    application.run_polling(allowed_updates=["message", "channel_post", "callback_query"])


if __name__ == "__main__":
    main()
