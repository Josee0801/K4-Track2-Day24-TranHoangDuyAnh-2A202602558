# Verification - before submission

- OS / Python / Gitleaks version: Windows PowerShell; Python 3.10.11 in this run; Gitleaks 8.30.1 from `.\tools\gitleaks\gitleaks.exe version`.
- `python -m pytest tests/ -q --basetemp=.pytest_tmp`: `33 passed in 7.84s`.
- CP3a PII metrics from `python -m pytest tests/test_pii.py -s`: `gold=118 pred=118 tp=118`, `precision=1.000 recall=1.000`.
- CP4 current scan: `gitleaks dir --config .gitleaks.toml --redact --verbose .` -> `no leaks found`.
- CP4 history scan: `gitleaks git --config .gitleaks.toml --redact --verbose .` -> expected exit code 1, one synthetic finding `lab24-synthetic-token` at commit `1bdd849`, file `lab-fake-secret.txt:1`.
- `python -m pip install --require-hashes -r requirements.lock`: success, all requirements already satisfied with hashes.
- `pre-commit run --all-files`: first needed `PRE_COMMIT_HOME` inside the repo because `C:\Users\admin\.cache` was not writable; after adding `tools/gitleaks` to PATH, hook ran and failed as expected on the lab's historical synthetic token `lab24-synthetic-token` (`10 commits scanned`, one finding at `lab-fake-secret.txt:1`).
- Ledger verify: `python -c "from agent.ledger import verify; from pathlib import Path; print(verify(Path('reports/ledger.jsonl')))"` -> `True`.
- Replay evidence: `reports/attack-before.log` contains synthetic `KH-000999`; `reports/attack-after.log` is 0 bytes after containment; `reports/ledger.jsonl:23` has deny for `http_post`.
- Cac loi con lai: none for required pytest suite. Pre-commit failure is the expected CP4 history finding, not a real credential; current tree scan is clean.
