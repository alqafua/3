"""Parses closed-trade messages posted in the signals group.

Expected formats (either can carry extra emoji/wording around them; the
parser only anchors on the pair tag and the Profit:/Loss: percentage line,
so it tolerates minor template variations):

    #CLO/USDT All targets achieved 😎
    Profit: 300.4172% 📈
    Period: 2 days 15 hr ⏰

    #SPX/USDT Stop Target Hit ⛔
    Loss: 600.0408% 📉
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

PAIR_RE = re.compile(r"#([A-Za-z0-9]+/[A-Za-z0-9]+)")
PROFIT_RE = re.compile(r"Profit:\s*([\d.]+)\s*%")
LOSS_RE = re.compile(r"Loss:\s*([\d.]+)\s*%")
PERIOD_RE = re.compile(r"Period:\s*([^\n⏰]+)")


@dataclass
class ParsedTrade:
    pair: str
    is_win: bool
    percent: float
    duration_text: Optional[str]


def parse_close_message(text: str) -> Optional[ParsedTrade]:
    if not text:
        return None

    pair_match = PAIR_RE.search(text)
    if not pair_match:
        return None
    pair = pair_match.group(1)

    duration_match = PERIOD_RE.search(text)
    duration_text = duration_match.group(1).strip() if duration_match else None

    profit_match = PROFIT_RE.search(text)
    if profit_match:
        return ParsedTrade(pair=pair, is_win=True, percent=float(profit_match.group(1)), duration_text=duration_text)

    loss_match = LOSS_RE.search(text)
    if loss_match:
        return ParsedTrade(pair=pair, is_win=False, percent=float(loss_match.group(1)), duration_text=duration_text)

    return None
