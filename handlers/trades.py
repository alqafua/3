"""Closed-trade tracking: auto-forwards winning closes to the public
channel, and builds the daily report / /t / Statistics outputs."""

from __future__ import annotations

import logging
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import config
import database
from reports import build_stats_by_pair_text, build_summary_text
from trade_parser import parse_close_message

logger = logging.getLogger(__name__)

TZ = ZoneInfo(config.REPORT_TIMEZONE)
UTC = ZoneInfo("UTC")


def _local_day_bounds(day: date) -> tuple[datetime, datetime]:
    """Returns (start, end) of a local calendar day as naive UTC datetimes,
    matching the naive-UTC convention used elsewhere in database.py."""
    start_local = datetime.combine(day, time.min, tzinfo=TZ)
    end_local = start_local + timedelta(days=1)
    start_utc = start_local.astimezone(UTC).replace(tzinfo=None)
    end_utc = end_local.astimezone(UTC).replace(tzinfo=None)
    return start_utc, end_utc


async def group_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Listens on the private trades group. Records every closed trade;
    auto-forwards wins only to the public channel, never losses."""
    message = update.effective_message
    if not message or not message.text:
        return

    parsed = parse_close_message(message.text)
    if parsed is None:
        return

    database.add_closed_trade(
        pair=parsed.pair,
        is_win=parsed.is_win,
        percent=parsed.percent,
        duration_text=parsed.duration_text,
        raw_message=message.text,
    )

    if parsed.is_win and config.PUBLIC_CHANNEL_ID:
        try:
            await context.bot.forward_message(
                chat_id=config.PUBLIC_CHANNEL_ID,
                from_chat_id=message.chat_id,
                message_id=message.message_id,
            )
        except TelegramError as exc:
            logger.warning("Failed to forward winning trade to public channel: %s", exc)


def _report_keyboard(report_day: date) -> InlineKeyboardMarkup | None:
    previous_report = database.get_daily_report(report_day - timedelta(days=1))
    if previous_report is None:
        return None

    internal_id = str(previous_report.chat_id)
    if internal_id.startswith("-100"):
        internal_id = internal_id[4:]
    link = f"https://t.me/c/{internal_id}/{previous_report.message_id}"

    return InlineKeyboardMarkup([[InlineKeyboardButton("◀️ اليوم السابق", url=link)]])


async def send_daily_report(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Runs at local midnight: reports on the day that just ended, pins it,
    unpins the previous day's report, and links back to it."""
    if not config.PUBLIC_CHANNEL_ID:
        return

    report_day = datetime.now(TZ).date() - timedelta(days=1)
    start_utc, end_utc = _local_day_bounds(report_day)
    trades = database.get_trades_between(start_utc, end_utc)

    title = f"📊 تقرير صفقات يوم {report_day.strftime('%Y-%m-%d')}"
    text = build_summary_text(trades, title)
    keyboard = _report_keyboard(report_day)

    try:
        sent = await context.bot.send_message(
            chat_id=config.PUBLIC_CHANNEL_ID,
            text=text,
            reply_markup=keyboard,
        )
    except TelegramError as exc:
        logger.error("Failed to send daily report: %s", exc)
        return

    previous_report = database.get_daily_report(report_day - timedelta(days=1))
    database.save_daily_report(report_day, config.PUBLIC_CHANNEL_ID, sent.message_id)

    try:
        await context.bot.pin_chat_message(
            chat_id=config.PUBLIC_CHANNEL_ID,
            message_id=sent.message_id,
            disable_notification=True,
        )
        if previous_report is not None:
            await context.bot.unpin_chat_message(
                chat_id=config.PUBLIC_CHANNEL_ID,
                message_id=previous_report.message_id,
            )
    except TelegramError as exc:
        logger.warning("Failed to pin/unpin daily report: %s", exc)


async def today_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/t — snapshot of today's results so far, sent back to the caller."""
    today = datetime.now(TZ).date()
    start_utc, _ = _local_day_bounds(today)
    end_utc = datetime.utcnow()
    trades = database.get_trades_between(start_utc, end_utc)

    title = f"📊 نتائج اليوم حتى الآن ({today.strftime('%Y-%m-%d')})"
    text = build_summary_text(trades, title)
    await update.message.reply_text(text)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/stats — all-time per-pair breakdown."""
    trades = database.get_all_closed_trades()
    text = build_stats_by_pair_text(trades, "📊 إحصائيات الصفقات (كل الأوقات)")
    await update.message.reply_text(text)


async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Statistics button in the bot's main menu."""
    query = update.callback_query
    await query.answer()
    trades = database.get_all_closed_trades()
    text = build_stats_by_pair_text(trades, "📊 إحصائيات الصفقات (كل الأوقات)")
    await context.bot.send_message(chat_id=query.message.chat_id, text=text)
