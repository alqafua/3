"""Payment screenshot handling: automatic on-chain verification with a
manual-review fallback for the admin (used for internal Binance UID
transfers and unclear screenshots)."""

import logging
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

import config
import database
from handlers.plans import create_invite_link
from keyboards import admin_review_keyboard
from notifications import notify_sale
from payment_verification import verify_payment_screenshot
from texts import TEXTS

logger = logging.getLogger(__name__)


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    db_user = database.get_user(user.id)
    lang = (db_user.language if db_user else None) or "ar"
    t = TEXTS[lang]

    if not db_user or db_user.status != "pending_payment" or not db_user.plan:
        await update.message.reply_text(t["no_pending_payment"])
        return

    plan = db_user.plan
    expected_amount = config.PLAN_PRICES.get(plan)
    if expected_amount is None:
        await update.message.reply_text(t["generic_error"])
        return

    await update.message.reply_text(t["processing_screenshot"])

    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    image_bytes = bytes(await photo_file.download_as_bytearray())

    try:
        result = verify_payment_screenshot(image_bytes, expected_amount)
    except Exception:  # noqa: BLE001 - never let a verification bug drop a real customer
        logger.exception("Payment verification crashed for user %s", user.id)
        result = None

    duplicate = bool(result and result.success and result.txid and database.is_txid_used(result.txid))

    if result and result.success and result.txid and not duplicate:
        expires_at = datetime.utcnow() + timedelta(days=config.PLAN_DURATIONS_DAYS[plan])
        invite_link = await create_invite_link(context)
        database.activate_subscription(user.id, plan, expires_at, invite_link)
        database.mark_txid_used(result.txid, result.network, user.id)

        await update.message.reply_text(
            t["payment_verified"].format(
                plan=t.get(f"plan_name_{plan}", plan),
                expires_at=expires_at.strftime("%Y-%m-%d"),
                invite_link=invite_link,
            )
        )
        amount_display = f"${result.amount:.2f} ({result.network.upper()}) — تحقق تلقائي"
        await notify_sale(context, user.id, user.username, t.get(f"plan_name_{plan}", plan), amount_display)
        return

    reason = "duplicate_txid" if duplicate else (result.reason if result else "verification_crashed")

    await update.message.reply_text(t["payment_pending_review"])

    caption = (
        "طلب اشتراك جديد يحتاج مراجعة يدوية / New subscription request needs manual review\n"
        f"User: {user.id} (@{user.username or '-'})\n"
        f"Plan: {plan} (${expected_amount})\n"
        f"Reason: {reason}"
    )
    await context.bot.send_photo(
        chat_id=config.ADMIN_CHAT_ID,
        photo=photo.file_id,
        caption=caption,
        reply_markup=admin_review_keyboard(user.id),
    )


async def admin_decision_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # callback_data is "admin_approve_<user_id>" or "admin_reject_<user_id>"
    _, action, user_id_str = query.data.split("_", 2)
    target_user_id = int(user_id_str)

    db_user = database.get_user(target_user_id)
    lang = (db_user.language if db_user else None) or "ar"
    t = TEXTS[lang]
    base_caption = query.message.caption or ""

    if action == "approve":
        plan = (db_user.plan if db_user else None) or "monthly"
        expires_at = datetime.utcnow() + timedelta(days=config.PLAN_DURATIONS_DAYS.get(plan, 30))
        invite_link = await create_invite_link(context)
        database.activate_subscription(target_user_id, plan, expires_at, invite_link)

        await context.bot.send_message(
            chat_id=target_user_id,
            text=t["payment_verified"].format(
                plan=t.get(f"plan_name_{plan}", plan),
                expires_at=expires_at.strftime("%Y-%m-%d"),
                invite_link=invite_link,
            ),
        )
        amount_display = f"${config.PLAN_PRICES.get(plan, 0):g} — موافقة يدوية"
        await notify_sale(
            context,
            target_user_id,
            db_user.username if db_user else None,
            t.get(f"plan_name_{plan}", plan),
            amount_display,
        )
        await query.edit_message_caption(caption=f"{base_caption}\n\n✅ تم التفعيل يدويًا / Approved by admin")
        return

    if db_user:
        database.set_status(target_user_id, "new")
    await context.bot.send_message(chat_id=target_user_id, text=t["payment_rejected"])
    await query.edit_message_caption(caption=f"{base_caption}\n\n❌ تم الرفض / Rejected by admin")
