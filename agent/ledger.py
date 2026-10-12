"""Append-only JSONL audit ledger with a local hash chain."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ZERO_HASH = "0" * 64


def _hash_entry(entry: dict) -> str:
    payload = {key: value for key, value in entry.items() if key != "hash"}
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _last_hash(path: Path) -> str:
    if not path.exists():
        return ZERO_HASH
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return ZERO_HASH
    try:
        return json.loads(lines[-1]).get("hash", ZERO_HASH)
    except json.JSONDecodeError:
        return ZERO_HASH


def append(entry: dict, path: Path) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    record = dict(entry)
    record["prev_hash"] = _last_hash(path)
    record["hash"] = _hash_entry(record)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def verify(path: Path) -> bool:
    if not path.exists():
        return True

    expected_prev = ZERO_HASH
    try:
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for line in lines:
            record = json.loads(line)
            if not record.get("reason"):
                return False
            if record.get("prev_hash") != expected_prev:
                return False
            stored_hash = record.get("hash")
            if not stored_hash or stored_hash != _hash_entry(record):
                return False
            expected_prev = stored_hash
    except (json.JSONDecodeError, OSError):
        return False
    return True
