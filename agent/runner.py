"""CP3c/3d runner with OBO checks and trifecta split.

Run A reads untrusted documents only. Run B receives typed ticket IDs derived
from filenames and uses trusted customer metadata to decide which records may be
read. Every tool call goes through policy and ledger before execution.
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agent import ledger, tools
from agent.policy import PolicyContext, check


REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
DEFAULT_LEDGER_PATH = REPORTS_DIR / "ledger.jsonl"
CUSTOMERS_FILE = Path(__file__).resolve().parent.parent / "data" / "customers.json"
AGENT_ID = "lab24-agent"
RUN_A_SCOPES = ("search_docs",)
RUN_B_SCOPES = ("read_customer",)
EGRESS_SCOPES = ("http_post",)
TICKET_RE = re.compile(r"^ticket-(\d+)")


class RunnerScaffoldPending(NotImplementedError):
    """Kept for compatibility; no longer raised once this runner is implemented."""


def _ledger_path(log_dir: Path | None) -> Path:
    return (log_dir or REPORTS_DIR) / "ledger.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _expiry() -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()


def _args_hash(args: dict) -> str:
    encoded = json.dumps(args, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _audit(
    path: Path,
    *,
    run_id: str,
    tool: str,
    args: dict,
    classification: str,
    decision: str,
    reason: str,
    principal_id: str,
    expires_at: str,
) -> None:
    ledger.append(
        {
            "ts": _now(),
            "agent_id": AGENT_ID,
            "run_id": run_id,
            "tool": tool,
            "args_hash": _args_hash(args),
            "classification": classification,
            "decision": decision,
            "reason": reason,
            "on_behalf_of": principal_id,
            "expires_at": expires_at,
        },
        path,
    )


def _policy_call(
    ledger_file: Path,
    *,
    run_id: str,
    principal_id: str,
    expires_at: str,
    tool_name: str,
    args: dict,
    classification: str,
    purpose: str,
    owner: str,
    egress_enabled: bool,
    agent_scopes: tuple[str, ...],
    parent_scopes: tuple[str, ...] = (),
    delegation_depth: int = 0,
) -> tuple[bool, str]:
    ctx = PolicyContext(
        data_classification=classification,
        request_purpose=purpose,
        agent_owner=owner,
        delegation_depth=delegation_depth,
        egress_enabled=egress_enabled,
        principal_id=principal_id,
        requested_tool=tool_name,
        agent_scopes=agent_scopes,
        parent_scopes=parent_scopes,
        expires_at=expires_at,
    )
    allowed, reason = check(ctx)
    _audit(
        ledger_file,
        run_id=run_id,
        tool=tool_name,
        args=args,
        classification=classification,
        decision="allow" if allowed else "deny",
        reason=reason,
        principal_id=principal_id,
        expires_at=expires_at,
    )
    return allowed, reason


def _ticket_ids_from_docs(docs: list[dict]) -> list[int]:
    ids: list[int] = []
    for doc in docs:
        match = TICKET_RE.match(str(doc.get("id", "")))
        if match:
            ids.append(int(match.group(1)))
    return sorted(set(ids))


def _customer_ids_for_tickets(ticket_ids: list[int]) -> list[str]:
    customers = json.loads(CUSTOMERS_FILE.read_text(encoding="utf-8"))
    wanted = set(ticket_ids)
    ids = [
        customer["customer_id"]
        for customer in customers
        if wanted.intersection(set(customer.get("related_tickets", [])))
    ]
    return sorted(set(ids))


def handle(message: str, llm, log_dir: Path | None = None, principal_id: str = "support_l1") -> str:
    ledger_file = _ledger_path(log_dir)
    run_token = uuid.uuid4().hex
    run_a_id = f"{run_token}:run-a"
    run_b_id = f"{run_token}:run-b"
    expires_at = _expiry()

    allowed, _ = _policy_call(
        ledger_file,
        run_id=run_a_id,
        principal_id=principal_id,
        expires_at=expires_at,
        tool_name="search_docs",
        args={"query": message},
        classification="internal",
        purpose="summarize-tickets",
        owner=f"{AGENT_ID}/run-a",
        egress_enabled=False,
        agent_scopes=RUN_A_SCOPES,
    )
    docs = tools.search_docs(message) if allowed else []

    combined_text = "\n\n".join(d["text"] for d in docs)
    injected = llm.find_injection(combined_text)
    ticket_ids = _ticket_ids_from_docs(docs)
    customer_ids = _customer_ids_for_tickets(ticket_ids)

    collected: list[dict] = []
    for customer_id in customer_ids:
        allowed, _ = _policy_call(
            ledger_file,
            run_id=run_b_id,
            principal_id=principal_id,
            expires_at=expires_at,
            tool_name="read_customer",
            args={"customer_id": customer_id},
            classification="restricted",
            purpose="support-reply",
            owner=f"{AGENT_ID}/run-b",
            egress_enabled=False,
            agent_scopes=RUN_B_SCOPES,
        )
        if not allowed:
            continue
        try:
            collected.append(tools.read_customer(customer_id))
        except tools.ToolError:
            continue

    if injected is not None and collected:
        allowed, _ = _policy_call(
            ledger_file,
            run_id=run_b_id,
            principal_id=principal_id,
            expires_at=expires_at,
            tool_name="http_post",
            args={"url": injected.target_url, "record_count": len(collected)},
            classification="restricted",
            purpose="support-reply",
            owner=f"{AGENT_ID}/run-b",
            egress_enabled=True,
            agent_scopes=EGRESS_SCOPES,
        )
        if allowed:
            tools.http_post(injected.target_url, {"records": collected})

    return llm.summarize(docs)
