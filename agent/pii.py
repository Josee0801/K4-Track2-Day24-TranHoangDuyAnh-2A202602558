"""CP3a - PII detection and redaction for the lab.

The detector is intentionally small and deterministic: it uses context-aware
regexes for Vietnamese CCCD, phone numbers, bank accounts, and email addresses.
"""
from __future__ import annotations

import re


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
CCCD_RE = re.compile(r"(?i)\bCCCD\D{0,60}(\d{12})\b")
PHONE_RE = re.compile(
    r"(?i)\b(?:SĐT|SDT|Số điện thoại|So dien thoai|phone)\D{0,60}(0(?:[\s.-]?\d){9,10})\b"
)
BANK_RE = re.compile(r"(?i)\b(?:STK|so tai khoan|tai khoan)\D{0,60}(\d(?:[\s.-]?\d){7,15})\b")


def _digit_count(value: str) -> int:
    return sum(ch.isdigit() for ch in value)


def _add_match(entities: list[dict], pii_type: str, start: int, end: int) -> None:
    if start < end:
        entities.append({"type": pii_type, "start": start, "end": end})


def detect(text: str) -> list[dict]:
    """Return PII spans as {"type", "start", "end"} dictionaries."""
    entities: list[dict] = []

    for match in EMAIL_RE.finditer(text):
        _add_match(entities, "EMAIL", match.start(), match.end())

    for match in CCCD_RE.finditer(text):
        _add_match(entities, "VN_CCCD", match.start(1), match.end(1))

    for match in PHONE_RE.finditer(text):
        value = match.group(1)
        if 10 <= _digit_count(value) <= 11:
            _add_match(entities, "VN_PHONE", match.start(1), match.end(1))

    for match in BANK_RE.finditer(text):
        value = match.group(1)
        if 8 <= _digit_count(value) <= 16:
            _add_match(entities, "VN_BANK_ACCOUNT", match.start(1), match.end(1))

    return sorted(entities, key=lambda item: (item["start"], item["end"], item["type"]))


def redact(text: str) -> str:
    """Replace every detected PII span with a typed redaction marker."""
    redacted = text
    for entity in sorted(detect(text), key=lambda item: item["start"], reverse=True):
        replacement = f"[REDACTED_{entity['type']}]"
        redacted = redacted[: entity["start"]] + replacement + redacted[entity["end"] :]
    return redacted
