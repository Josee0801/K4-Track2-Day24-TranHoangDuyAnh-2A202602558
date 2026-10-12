# Secrets incident note - CP4

- Scanner va phien ban: Gitleaks 8.30.1, chay bang `.\tools\gitleaks\gitleaks.exe`.
- Commit chua token gia: `1bdd849` (short SHA cua seed commit).
- File, rule va ket qua quet lich su: `lab-fake-secret.txt:1`, rule id `lab24-synthetic-token`, fingerprint bat dau bang `1bdd849:lab-fake-secret.txt:lab24-synthetic-token:1`. Lenh `gitleaks git --config .gitleaks.toml --redact --verbose .` tra exit code 1 vi tim thay token synthetic nay trong history.
- Ket qua quet file hien tai: `gitleaks dir --config .gitleaks.toml --redact --verbose .` bao `no leaks found` sau khi loai cac artifact local `.venv`, `.pytest_cache`, va `tools/gitleaks` trong `.gitleaks.toml`.
- Day la token gia cua lab, khong phai credential that. Neu day la credential that thi phai thu hoi/rotate ngay tai he thong phat hanh secret, kiem tra log su dung, cap lai credential moi, va thong bao owner lien quan.
- Xoa file khoi HEAD khong du vi secret van con trong Git history va co the da bi clone/cache. Pin dependency, hash lock, va pre-commit hook giup giam rui ro tai dien, nhung khong thay the buoc rotate/thu hoi khi secret da lo.
