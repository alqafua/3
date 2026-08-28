"""Builds the plain-text summaries used by the daily report, /t and the
Statistics button."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database import ClosedTrade


def _format_trade_line(trade: "ClosedTrade") -> str:
    icon = "✅" if trade.is_win else "🚫"
    label = "ربح" if trade.is_win else "خسارة"
    return f"{icon} #{trade.pair} — {label} {trade.percent:.2f}%"


def build_summary_text(trades: list["ClosedTrade"], title: str) -> str:
    """A chronological list of trades for a single period (daily report / /t)."""
    if not trades:
        return f"{title}\n\nلا توجد صفقات مغلقة."

    wins = [t for t in trades if t.is_win]
    losses = [t for t in trades if not t.is_win]
    win_rate = (len(wins) / len(trades)) * 100

    lines = [title, ""]
    lines.extend(_format_trade_line(t) for t in trades)
    lines.append("")
    lines.append("────────────────")
    lines.append(f"عدد الصفقات: {len(trades)}")
    lines.append(f"✅ رابحة: {len(wins)}")
    lines.append(f"🚫 خاسرة: {len(losses)}")
    lines.append(f"📈 نسبة النجاح: {win_rate:.1f}%")

    return "\n".join(lines)


def build_stats_by_pair_text(trades: list["ClosedTrade"], title: str) -> str:
    """Per-pair breakdown used by the Statistics button (all-time)."""
    if not trades:
        return f"{title}\n\nلا توجد صفقات مسجلة بعد."

    by_pair: dict[str, list["ClosedTrade"]] = {}
    for trade in trades:
        by_pair.setdefault(trade.pair, []).append(trade)

    lines = [title, ""]
    for pair, pair_trades in sorted(by_pair.items()):
        wins = [t for t in pair_trades if t.is_win]
        losses = [t for t in pair_trades if not t.is_win]
        net = sum(t.percent if t.is_win else -t.percent for t in pair_trades)
        win_rate = (len(wins) / len(pair_trades)) * 100
        sign = "+" if net >= 0 else ""
        lines.append(
            f"🔸 #{pair}: {sign}{net:.2f}% | صفقات: {len(pair_trades)} "
            f"(✅{len(wins)} / 🚫{len(losses)}) | نجاح: {win_rate:.1f}%"
        )

    total = len(trades)
    total_wins = sum(1 for t in trades if t.is_win)
    total_losses = total - total_wins
    total_win_rate = (total_wins / total) * 100

    lines.append("")
    lines.append("────────────────")
    lines.append(f"إجمالي الصفقات: {total}")
    lines.append(f"✅ رابحة: {total_wins}")
    lines.append(f"🚫 خاسرة: {total_losses}")
    lines.append(f"📈 نسبة النجاح الكلية: {total_win_rate:.1f}%")

    return "\n".join(lines)
