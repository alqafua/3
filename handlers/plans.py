"""Plan selection: trial activation and paid-plan payment instructions."""

import logging
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

import config
import database
from texts import TEXTS

logger = logging.getLogger(__name__)

PLAN_CALLBACK_MAP = {
    "plan_trial": "trial",
    "plan_monthly": "monthly",
    "plan_quarterly": "quarterly",
    "plan_yearly": "yearly",
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
        t["payment_instructions"].format(
            price=price,
            trc20_wallet=config.TRC20_WALLET,
            bsc_wallet=config.BSC_WALLET,
            binance_uid=config.BINANCE_UID,
        ),
        parse_mode="HTML",
    )
