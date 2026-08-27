"""Plan selection: trial activation and paid-plan payment instructions."""

import logging
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

import config
import database
from keyboards import payment_method_keyboard
from texts import TEXTS

logger = logging.getLogger(__name__)

PLAN_CALLBACK_MAP = {
    "plan_trial": "trial",
    "plan_monthly": "monthly",
    "plan_quarterly": "quarterly",
    "plan_yearly": "yearly",
}

PAYMENT_METHODS = {
    "trc20": ("wallet_label_trc20", "payment_footer_trc20", "TRC20_WALLET"),
    "bep20": ("wallet_label_bep20", "payment_footer_bep20", "BSC_WALLET"),
    "binance": ("wallet_label_binance", "payment_footer_binance", "BINANCE_UID"),
}


async def create_invite_link(context: ContextTypes.DEFAULT_TYPE) -> str:
    invite = await context.bot.create_chat_invite_link(
        chat_id=config.VIP_CHANNEL_ID,
        member_limit=1,
    )
    return invite.invite_link


async def activate_trial(context: ContextTypes.DEFAULT_TYPE, user_id: int, lang: str) -> None:
    expires_at = datetime.utcnow() + timedelta(days=config.TRIAL_DAYS)
    invite_link = await create_invite_link(context)
    database.activate_subscription(user_id, "trial", expires_at, invite_link)

    t = TEXTS[lang]
    await context.bot.send_message(
        chat_id=user_id,
        text=t["trial_activated"].format(days=config.TRIAL_DAYS, invite_link=invite_link),
    )


async def plan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    plan = PLAN_CALLBACK_MAP.get(query.data)
    if plan is None:
        return

    db_user = database.get_user(query.from_user.id)
    lang = (db_user.language if db_user else None) or "ar"
    t = TEXTS[lang]

    if plan == "trial":
        if db_user and db_user.used_trial:
            await query.edit_message_text(t["trial_already_used"])
            return
        await query.edit_message_text(t["trial_activating"])
        await activate_trial(context, query.from_user.id, lang)
        return

    database.set_pending_plan(query.from_user.id, plan)
    price = config.PLAN_PRICES[plan]

    await query.edit_message_text(
        t["payment_intro"].format(price=price),
        reply_markup=payment_method_keyboard(lang),
        parse_mode="HTML",
    )


async def payment_method_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    method = query.data.split("_", 1)[1]
    label_key, footer_key, config_attr = PAYMENT_METHODS[method]
    wallet_value = getattr(config, config_attr)

    db_user = database.get_user(query.from_user.id)
    lang = (db_user.language if db_user else None) or "ar"
    t = TEXTS[lang]

    await query.answer(text=t["payment_method_sent"])

    chat_id = query.from_user.id
    await context.bot.send_message(chat_id=chat_id, text=t[label_key])
    await context.bot.send_message(chat_id=chat_id, text=wallet_value)
    await context.bot.send_message(chat_id=chat_id, text=t[footer_key], parse_mode="HTML")
