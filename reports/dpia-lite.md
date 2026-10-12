# DPIA-lite - CP5

1. Loai du lieu va phan loai: Lab dung du lieu synthetic trong `data/customers.json`, gom customer_id, name, CCCD, phone, bank_account, email, related_tickets. CCCD, phone, bank_account, email duoc xem la PII; customer record doc bang `read_customer` duoc xu ly nhu `restricted`.

2. Muc dich xu ly va principal: `support_l1` chi duoc `search_docs`; `dpo` duoc `read_customer` cho purpose `support-reply`. Policy deny unknown principal, purpose sai, scope thieu, TTL het han, va moi truong `restricted + egress`.

3. Du lieu di qua run/tool/endpoint: Run A goi `search_docs` de doc corpus untrusted va chi truyen ticket id lay tu ten file. Run B map ticket id sang customer qua `related_tickets` trong `data/customers.json`, check policy ngay truoc `read_customer`, va khong lay customer id tu free text attacker. Endpoint egress duy nhat cua lab la sink localhost `http://127.0.0.1:10024/reconcile`; sau containment, `http_post` bi deny nen `reports/attack-after.log` rong.

4. Bang chung deny/allow va gioi han mock: `reports/ledger.jsonl:23` co `tool=http_post`, `decision=deny`, `reason=restricted data cannot be used in an egress-enabled tool call`, `on_behalf_of=dpo`. `reports/attack-before.log:1` chung minh baseline leak synthetic `KH-000999`; `reports/attack-after.log` dai 0 byte sau replay. Gioi han: `--mock` la deterministic LLM mo phong, principal la fixture, sink chi la localhost, ledger hash chain trong file khong phat hien xoa dong cuoi neu khong co moc tin cay ben ngoai.
