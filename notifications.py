"""Admin notifications for leads (plan selected, not yet paid) and sales
(subscription activated), sent to config.ADMIN_CHAT_ID."""

from __future__ import annotations

from typing import Optional

from telegram.ext import ContextTypes

import config


def _user_line(user_id: int, username: Optional[str]) -> str:
    handle = f"@{username}" if username else "بدون يوزر"
    return f'<a href="tg://user?id={user_id}">{handle}</a> (id: <code>{user_id}</code>)'


async def notify_lead(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    username: Optional[str],
    plan_label: str,
    price: float,
) -> None:
    if not config.ADMIN_CHAT_ID:
        return
    text = (
        "🔔 <b>عميل محتمل</b> — اختار خطة ولسا ما دفع\n\n"
        f"👤 {_user_line(user_id, username)}\n"
        f"📦 الخطة: {plan_label} (${price:g})\n\n"
        "تواصل معه لو تأخر يكمل الدفع."
    )
    await context.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=text, parse_mode="HTML")


async def notify_sale(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    username: Optional[str],
    plan_label: str,
    amount_display: str,
) -> None:
    if not config.ADMIN_CHAT_ID:
        return
    text = (
        "💰 <b>اشتراك جديد</b>\n\n"
        f"👤 {_user_line(user_id, username)}\n"
        f"📦 الخطة: {plan_label}\n"
        f"💵 المبلغ: {amount_display}"
    )
    await context.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=text, parse_mode="HTML")
