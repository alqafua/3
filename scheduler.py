"""Hourly job: expire subscriptions and remove users from the VIP channel."""

import logging
from datetime import datetime

from telegram.error import TelegramError
from telegram.ext import ContextTypes

import config
import database
from texts import TEXTS

logger = logging.getLogger(__name__)


async def check_expired_subscriptions(context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.utcnow()
    expired_users = database.get_expired_users(now)

    for user in expired_users:
        try:
            await context.bot.ban_chat_member(chat_id=config.VIP_CHANNEL_ID, user_id=user.user_id)
            await context.bot.unban_chat_member(chat_id=config.VIP_CHANNEL_ID, user_id=user.user_id)
        except TelegramError as exc:
            logger.warning("Failed to remove expired user %s from channel: %s", user.user_id, exc)

        database.mark_expired(user.user_id)

        lang = user.language or "ar"
        try:
            await context.bot.send_message(
                chat_id=user.user_id,
                text=TEXTS[lang]["subscription_expired_notice"],
            )
        except TelegramError as exc:
            logger.warning("Failed to notify expired user %s: %s", user.user_id, exc)
