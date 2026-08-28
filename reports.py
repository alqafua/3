"""Builds the plain-text summaries used by the daily report, /t and the
Statistics button.

Matches the reference channel's own report style: a flat list of trades
("SYMBOL : ±percent%", no icons) followed by an aggregate stats box. Kept
bilingual (AR/EN) since this business runs a bilingual channel and bot."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database import ClosedTrade

SEPARATOR = "➖➖➖➖➖➖➖➖➖➖"


def _symbol(pair: str) -> str:
    """Base coin symbol only, no "#" and no "/USDT" quote suffix."""
    return pair.split("/")[0]


def _format_trade_line(trade: "ClosedTrade") -> str:
    sign = "+" if trade.is_win else "-"
    return f"{_symbol(trade.pair)} : {sign}{trade.percent:.2f}%"


def _build_report(trades: list["ClosedTrade"], title: str) -> str:
    if not trades:
        return f"{title}\n\n🚫 لا صفقات / No trades"

    wins = [t for t in trades if t.is_win]
    losses = [t for t in trades if not t.is_win]
    total = len(trades)
    win_rate = (len(wins) / total) * 100
    net_total = sum(t.percent if t.is_win else -t.percent for t in trades)
    avg_per_trade = net_total / total

    lines = [title, ""]
    lines.extend(_format_trade_line(t) for t in trades)
    lines.append("")
    lines.append(SEPARATOR)
    lines.append(f"💰 الربح الكلي / Total profit: {net_total:.2f}%")
    lines.append(f"📈 متوسط الربح لكل صفقة / Avg per trade: {avg_per_trade:.2f}%")
    lines.append(f"📡 عدد الإشارات / Signals: {total}")
    lines.append(f"🎯 نسبة النجاح / Win rate: {win_rate:.1f}%")
    lines.append(f"✅ الصفقات الناجحة / Wins: {len(wins)}")
    lines.append(f"🚫 الصفقات الفاشلة / Losses: {len(losses)}")

    return "\n".join(lines)


def build_summary_text(trades: list["ClosedTrade"], title: str) -> str:
    """Daily report / /t: chronological list of trades for a single period."""
    return _build_report(trades, title)


def build_stats_by_pair_text(trades: list["ClosedTrade"], title: str) -> str:
    """Statistics button / /stats: all-time list of trades."""
    return _build_report(trades, title)
