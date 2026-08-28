"""Builds the plain-text summaries used by the daily report, /t and the
Statistics button.

Kept language-neutral on purpose: emojis carry the meaning, and any label
that still needs text is written in both Arabic and English side by side
(this business runs a bilingual AR/EN channel and bot)."""

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
    trend = "📈" if trade.is_win else "📉"
    return f"{_symbol(trade.pair)}: {sign}{trade.percent:.2f}% {trend}"


def build_summary_text(trades: list["ClosedTrade"], title: str) -> str:
    """A chronological list of trades for a single period (daily report / /t)."""
    if not trades:
        return f"{title}\n\n🚫 لا صفقات / No trades"

    wins = [t for t in trades if t.is_win]
    losses = [t for t in trades if not t.is_win]
    win_rate = (len(wins) / len(trades)) * 100

    lines = [title, ""]
    lines.extend(_format_trade_line(t) for t in trades)
    lines.append("")
    lines.append(SEPARATOR)
    lines.append(f"🔢 الصفقات / Trades: {len(trades)}")
    lines.append(f"✅ رابحة / Wins: {len(wins)}")
    lines.append(f"🚫 خاسرة / Losses: {len(losses)}")
    lines.append(f"🎯 النجاح / Win rate: {win_rate:.1f}%")

    return "\n".join(lines)


def build_stats_by_pair_text(trades: list["ClosedTrade"], title: str) -> str:
    """Per-coin breakdown used by the Statistics button (all-time)."""
    if not trades:
        return f"{title}\n\n🚫 لا صفقات / No trades"

    by_symbol: dict[str, list["ClosedTrade"]] = {}
    for trade in trades:
        by_symbol.setdefault(_symbol(trade.pair), []).append(trade)

    lines = [title, ""]
    for symbol, symbol_trades in sorted(by_symbol.items()):
        wins = [t for t in symbol_trades if t.is_win]
        losses = [t for t in symbol_trades if not t.is_win]
        net = sum(t.percent if t.is_win else -t.percent for t in symbol_trades)
        win_rate = (len(wins) / len(symbol_trades)) * 100
        sign = "+" if net >= 0 else ""
        lines.append(
            f"🔸 {symbol} {sign}{net:.2f}% | 🔢{len(symbol_trades)} ✅{len(wins)} 🚫{len(losses)} 🎯{win_rate:.1f}%"
        )

    total = len(trades)
    total_wins = sum(1 for t in trades if t.is_win)
    total_losses = total - total_wins
    total_win_rate = (total_wins / total) * 100

    lines.append("")
    lines.append(SEPARATOR)
    lines.append(f"🔢 الإجمالي / Total: {total}")
    lines.append(f"✅ رابحة / Wins: {total_wins}")
    lines.append(f"🚫 خاسرة / Losses: {total_losses}")
    lines.append(f"🎯 النجاح / Win rate: {total_win_rate:.1f}%")

    return "\n".join(lines)
