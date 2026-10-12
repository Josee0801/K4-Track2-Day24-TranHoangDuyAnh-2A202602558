# Compliance mapping - CP5

Chua doi chieu van ban goc nen khong khang dinh dieu khoan phap ly cu the. Bang duoi chi map yeu cau quan tri/bao mat cua lab sang control va evidence ky thuat da lam.

| Nguon / yeu cau | Control da lam | Evidence file:line | Gioi han |
|---|---|---|---|
| Luat 91/2025/QH15 | Data minimization va ngan ro ri PII: PII regex gate, restricted data khong duoc di qua egress, attack sau containment rong. | `agent/pii.py:11`, `agent/pii.py:28`, `agent/policy.py:50`, `reports/attack-after.log:1` | Chua xac minh dieu khoan goc; lab dung du lieu synthetic, khong phai he thong production. |
| ND 356/2025/ND-CP | Access control theo principal/purpose/tool/scope/TTL; audit co reason va hash chain. | `agent/policy.py:56`, `agent/policy.py:61`, `agent/policy.py:67`, `agent/policy.py:74`, `agent/ledger.py:30`, `agent/ledger.py:40` | Principal trong `data/principals.json` chi la fixture mo phong, khong phai authentication that. |
| Luat AI 134/2025/QH15 | Kiem soat agent hanh dong thay nguoi dung: moi tool call di qua policy truoc execute, ledger ghi `on_behalf_of`, `agent_id`, `run_id`, `expires_at`. | `agent/runner.py:80`, `agent/runner.py:96`, `agent/runner.py:108`, `agent/runner.py:63`, `agent/runner.py:65`, `agent/runner.py:73`, `reports/ledger.jsonl:23` | Chua xac minh dieu khoan goc; mock LLM khong dai dien day du rui ro model production. |
| OWASP ASI01, ASI03, ASI04 | Prompt injection duoc replay bang 4 lure; trifecta split ngan free-text attacker quyet dinh customer; egress restricted bi deny; supply-chain scan bat token synthetic trong history va current scan sach. | `injection-corpus.md:17`, `agent/runner.py:123`, `agent/runner.py:132`, `agent/runner.py:192`, `reports/ledger.jsonl:23`, `.gitleaks.toml:6`, `.pre-commit-config.yaml:2`, `reports/secrets-incident.md:4` | Mapping OWASP o muc lab; khong thay the threat model va test production. |
