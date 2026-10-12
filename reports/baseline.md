# Baseline - checkpoint 1

1. Moi lan chay baseline chua co `agent_id`, `run_id`, hay danh tinh nguoi dung de kiem quyen: `_naive_loop(message, llm)` chi nhan `message` va `llm` (`agent/loop.py:27`). Khi `agent.runner.handle()` con la scaffold, `run_once()` fallback ve `_naive_loop(message, llm)` ma khong truyen `principal_id` vao baseline (`agent/loop.py:73-74`).

2. Truoc `http_post` khong co policy nao kiem muc dich, quyen, hay loai du lieu. Baseline doc ticket bang `search_docs`, dua toan van ticket vao `find_injection`, roi xu ly chi thi nam trong ticket nhu lenh: lay `customer_ids`, goi `read_customer()` (`agent/loop.py:31-39`) va neu co du lieu thi goi `http_post()` (`agent/loop.py:42-44`). Nguoi thuc su quyet dinh gui la ket qua `llm.find_injection(combined_text)`, khong phai policy.

3. Dong tao body POST la `tools.http_post(injected.target_url, {"records": collected})` (`agent/loop.py:44`). `http_post()` trong `agent/tools.py` chi gioi han URL ve localhost roi goi `requests.post(url, json=body, timeout=timeout)` (`agent/tools.py:76-84`); sink ghi body da nhan vao `reports/sink.log` tai `sink/sink.py:45-47`.
