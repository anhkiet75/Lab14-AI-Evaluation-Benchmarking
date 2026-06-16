# Reflection - NguyenVanPhuc

## Đóng góp kỹ thuật

- Xây dựng `engine/runner.py`: orchestrate toàn bộ benchmark pipeline từ load dataset đến export report.
- Implement `main.py` với CLI flags: `--dataset`, `--output-dir`, `--threshold`, `--dry-run`.
- Sinh `reports/summary.json` và `reports/benchmark_results.json` với đầy đủ per-case và aggregate metrics.
- Implement regression delta: so sánh kết quả với baseline run và flag khi score giảm > 10%.
- Xây dựng release gate logic: block release nếu pass rate < 70% hoặc avg score < 3.0.

## Quyết định kỹ thuật

- Thiết kế runner theo pipeline pattern: mỗi stage (retrieve → generate → judge → report) độc lập.
- Dùng `concurrent.futures.ThreadPoolExecutor` để chạy cases song song, giảm thời gian benchmark.
- Lưu intermediate results sau mỗi case để có thể resume khi bị interrupt.
- JSON report format thay vì CSV để dễ parse và nested metrics.

## Vấn đề gặp phải

- Race condition khi ghi intermediate results đồng thời, cần thêm file lock.
- Benchmark chậm khi agent và judge đều gọi API: 50 cases x 2 judges ≈ 150+ API calls.
- Baseline file không tồn tại ở lần chạy đầu tiên, cần handle gracefully.

## Bằng chứng kiểm thử

- `python main.py`: sinh đầy đủ `reports/summary.json`, `reports/benchmark_results.json`.
- Release gate hoạt động đúng: pass khi avg score ≥ 3.0 và pass rate ≥ 70%.
- Regression delta được tính và log ra console khi có baseline.
- `python check_lab.py`: pass kiểm tra output format.

## Cải tiến tiếp theo

- Thêm progress bar (tqdm) để theo dõi tiến trình benchmark real-time.
- Implement proper file locking cho intermediate results.
- Thêm `--resume` flag để tiếp tục từ case cuối cùng khi bị interrupt.
- Export thêm HTML report với charts cho dễ đọc.
