"""/start, language selection and /status."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

import database
from keyboards import language_keyboard, plans_keyboard
from texts import TEXTS

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    database.get_or_create_user(user.id, user.username)
    await update.message.reply_text(
        TEXTS["ar"]["choose_language"],
        reply_markup=language_keyboard(),
    )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    lang = "ar" if query.data == "lang_ar" else "en"
    database.set_language(query.from_user.id, lang)
    db_user = database.get_user(query.from_user.id)

    t = TEXTS[lang]
    show_trial = not (db_user and db_user.used_trial)

    await query.edit_message_text(
        t["welcome"],
        reply_markup=plans_keyboard(lang, show_trial),
        parse_mode="HTML",
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db_user = database.get_user(update.effective_user.id)
    lang = (db_user.language if db_user else None) or "ar"
    t = TEXTS[lang]

    if not db_user or db_user.status in ("new", "pending_payment"):
        await update.message.reply_text(t["status_none"])
        return

    if db_user.status == "active":
        plan_label = t.get(f"plan_name_{db_user.plan}", db_user.plan)
        expires_str = db_user.expires_at.strftime("%Y-%m-%d %H:%M UTC") if db_user.expires_at else "-"
        await update.message.reply_text(t["status_active"].format(plan=plan_label, expires_at=expires_str))
        return

    await update.message.reply_text(t["status_expired"])
