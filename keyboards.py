"""Inline keyboard builders."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import config
from texts import TEXTS


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
                InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            ],
            [
                InlineKeyboardButton(
                    "الدعم | Support",
                    url=f"https://t.me/{config.SUPPORT_USERNAME}",
                )
            ],
        ]
    )


def plans_keyboard(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(t["btn_monthly"], callback_data="plan_monthly")],
            [InlineKeyboardButton(t["btn_quarterly"], callback_data="plan_quarterly")],
            [InlineKeyboardButton(t["btn_yearly"], callback_data="plan_yearly")],
            [InlineKeyboardButton(t["btn_statistics"], callback_data="show_stats")],
        ]
    )


def payment_method_keyboard(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(t["btn_pay_trc20"], callback_data="paymethod_trc20")],
            [InlineKeyboardButton(t["btn_pay_bep20"], callback_data="paymethod_bep20")],
            [InlineKeyboardButton(t["btn_pay_binance"], callback_data="paymethod_binance")],
        ]
    )


def admin_review_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ تفعيل / Approve", callback_data=f"admin_approve_{user_id}"),
                InlineKeyboardButton("❌ رفض / Reject", callback_data=f"admin_reject_{user_id}"),
            ]
        ]
    )
