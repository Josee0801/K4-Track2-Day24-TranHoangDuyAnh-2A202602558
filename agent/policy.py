"""CP3b - policy checks for tool calls.

Every decision returns a non-empty reason so the runner can write complete
audit entries for both allow and deny outcomes.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PRINCIPALS_FILE = BASE_DIR / "data" / "principals.json"


@dataclass(frozen=True)
class PolicyContext:
    data_classification: str
    request_purpose: str
    agent_owner: str
    delegation_depth: int
    egress_enabled: bool
    principal_id: str = ""
    requested_tool: str = ""
    agent_scopes: tuple[str, ...] = ()
    parent_scopes: tuple[str, ...] = ()
    expires_at: str = ""


def _principals() -> dict:
    return json.loads(PRINCIPALS_FILE.read_text(encoding="utf-8"))


def _parse_expiry(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def check(context: PolicyContext) -> tuple[bool, str]:
    """Return (allow, reason) for the requested tool call."""
    if context.data_classification == "restricted" and context.egress_enabled:
        return False, "restricted data cannot be used in an egress-enabled tool call"

    if not context.principal_id:
        return True, "allowed: no principal supplied for baseline policy context"

    principals = _principals()
    principal = principals.get(context.principal_id)
    if principal is None:
        return False, f"unknown principal: {context.principal_id}"

    expires_at = _parse_expiry(context.expires_at)
    if expires_at is None:
        return False, "missing or invalid expires_at"
    if expires_at <= datetime.now(timezone.utc):
        return False, "authorization expired"

    if context.request_purpose not in principal.get("purposes", []):
        return False, f"purpose not allowed for principal: {context.request_purpose}"

    requested_tool = context.requested_tool
    if not requested_tool:
        return False, "missing requested_tool"

    allowed_tools = set(principal.get("allowed_tools", []))
    effective_tools = allowed_tools & set(context.agent_scopes)
    if context.delegation_depth > 0:
        effective_tools &= set(context.parent_scopes)

    if requested_tool not in effective_tools:
        return False, f"tool not allowed by effective scopes: {requested_tool}"

    return True, f"allowed {requested_tool} for {context.principal_id}"
