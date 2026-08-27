"""OCR extraction and on-chain payment verification.

Deliberately kept independent from any python-telegram-bot imports so it
can be tested / reused standalone.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

import pytesseract
import requests
from PIL import Image

import config

if config.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD

# A bare Tron txid is a 64-char hex string with no 0x prefix.
TRC20_TXID_RE = re.compile(r"\b[0-9a-fA-F]{64}\b")
# A BSC/EVM txid is 0x followed by 64 hex chars.
BEP20_TXID_RE = re.compile(r"\b0x[0-9a-fA-F]{64}\b")

USDT_TRC20_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
USDT_BEP20_CONTRACT = "0x55d398326f99059fF775485246999027B3197955"
TRANSFER_EVENT_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

TRONGRID_BASE = "https://api.trongrid.io"
BSCSCAN_BASE = "https://api.bscscan.com/api"

REQUEST_TIMEOUT = 15


@dataclass
class VerificationResult:
    success: bool
    network: Optional[str] = None
    txid: Optional[str] = None
    amount: Optional[float] = None
    reason: str = ""


def extract_text_from_image(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(image)


def _find_txid_candidates(text: str) -> list[tuple[str, str]]:
    """Return (network, txid) candidates, BEP20 (0x-prefixed) checked first."""
    candidates: list[tuple[str, str]] = []
    for match in BEP20_TXID_RE.finditer(text):
        candidates.append(("bep20", match.group(0)))
    for match in TRC20_TXID_RE.finditer(text):
        txid = match.group(0)
        if txid.lower().startswith("0x"):
            continue
        candidates.append(("trc20", txid))
    return candidates


def _trc20_wallet_hex() -> Optional[str]:
    if not config.TRC20_WALLET:
        return None
    try:
        from base58 import b58decode_check

        return b58decode_check(config.TRC20_WALLET).hex().lower()
    except Exception:
        return None


def _trc20_address_matches(to_address: str) -> bool:
    target_hex = _trc20_wallet_hex()
    if not target_hex:
        return False
    candidate = to_address.lower()
    if candidate.startswith("0x"):
        candidate = candidate[2:]
    if len(candidate) == 40:
        candidate = "41" + candidate
    return candidate == target_hex


def _verify_trc20(txid: str, expected_amount: float) -> VerificationResult:
    try:
        info_resp = requests.get(
            f"{TRONGRID_BASE}/wallet/gettransactioninfobyid",
            params={"value": txid},
            timeout=REQUEST_TIMEOUT,
        )
        info_resp.raise_for_status()
        info = info_resp.json()
    except Exception as exc:  # noqa: BLE001 - surface as a verification failure, not a crash
        return VerificationResult(False, "trc20", txid, None, f"tron_api_error: {exc}")

    if not info or info.get("receipt", {}).get("result") not in (None, "SUCCESS"):
        return VerificationResult(False, "trc20", txid, None, "transaction_not_found_or_failed")

    try:
        events_resp = requests.get(
            f"{TRONGRID_BASE}/v1/transactions/{txid}/events",
            timeout=REQUEST_TIMEOUT,
        )
        events_resp.raise_for_status()
        events = events_resp.json().get("data", [])
    except Exception as exc:  # noqa: BLE001
        return VerificationResult(False, "trc20", txid, None, f"tron_api_error: {exc}")

    for event in events:
        if event.get("event_name") != "Transfer":
            continue
        if event.get("contract_address") != USDT_TRC20_CONTRACT:
            continue
        result = event.get("result", {})
        to_address = result.get("to")
        raw_value = result.get("value")
        if to_address is None or raw_value is None:
            continue
        if not _trc20_address_matches(to_address):
            continue
        amount = Decimal(str(raw_value)) / Decimal(10**6)
        if abs(float(amount) - expected_amount) <= config.PAYMENT_AMOUNT_TOLERANCE:
            return VerificationResult(True, "trc20", txid, float(amount), "ok")
        return VerificationResult(False, "trc20", txid, float(amount), "amount_mismatch")

    return VerificationResult(False, "trc20", txid, None, "no_matching_transfer_event")


def _verify_bep20(txid: str, expected_amount: float) -> VerificationResult:
    try:
        status_resp = requests.get(
            BSCSCAN_BASE,
            params={
                "module": "transaction",
                "action": "gettxreceiptstatus",
                "txhash": txid,
                "apikey": config.BSCSCAN_API_KEY,
            },
            timeout=REQUEST_TIMEOUT,
        )
        status_resp.raise_for_status()
        status = status_resp.json().get("result", {}).get("status")
    except Exception as exc:  # noqa: BLE001
        return VerificationResult(False, "bep20", txid, None, f"bscscan_api_error: {exc}")

    if status != "1":
        return VerificationResult(False, "bep20", txid, None, "transaction_not_found_or_failed")

    try:
        receipt_resp = requests.get(
            BSCSCAN_BASE,
            params={
                "module": "proxy",
                "action": "eth_getTransactionReceipt",
                "txhash": txid,
                "apikey": config.BSCSCAN_API_KEY,
            },
            timeout=REQUEST_TIMEOUT,
        )
        receipt_resp.raise_for_status()
        receipt = receipt_resp.json().get("result")
    except Exception as exc:  # noqa: BLE001
        return VerificationResult(False, "bep20", txid, None, f"bscscan_api_error: {exc}")

    if not receipt:
        return VerificationResult(False, "bep20", txid, None, "receipt_not_found")

    target_wallet = config.BSC_WALLET.lower()
    for log in receipt.get("logs", []):
        if log.get("address", "").lower() != USDT_BEP20_CONTRACT.lower():
            continue
        topics = log.get("topics", [])
        if len(topics) < 3 or topics[0].lower() != TRANSFER_EVENT_TOPIC.lower():
            continue
        to_address = "0x" + topics[2][-40:]
        if to_address.lower() != target_wallet:
            continue
        raw_value = int(log.get("data", "0x0"), 16)
        amount = Decimal(raw_value) / Decimal(10**18)
        if abs(float(amount) - expected_amount) <= config.PAYMENT_AMOUNT_TOLERANCE:
            return VerificationResult(True, "bep20", txid, float(amount), "ok")
        return VerificationResult(False, "bep20", txid, float(amount), "amount_mismatch")

    return VerificationResult(False, "bep20", txid, None, "no_matching_transfer_log")


def verify_payment_screenshot(image_bytes: bytes, expected_amount: float) -> VerificationResult:
    """Extract a TXID from the screenshot and verify it on-chain.

    Internal Binance UID transfers never appear on a public blockchain, so
    they will always fall through to "no_txid_found" here and get routed
    to manual admin review by the caller - this is expected, not a bug.
    """
    try:
        text = extract_text_from_image(image_bytes)
    except Exception as exc:  # noqa: BLE001
        return VerificationResult(False, None, None, None, f"ocr_error: {exc}")

    candidates = _find_txid_candidates(text)
    if not candidates:
        return VerificationResult(False, None, None, None, "no_txid_found")

    last_result = VerificationResult(False, None, None, None, "no_txid_found")
    for network, txid in candidates:
        result = _verify_bep20(txid, expected_amount) if network == "bep20" else _verify_trc20(txid, expected_amount)
        if result.success:
            return result
        last_result = result
    return last_result
