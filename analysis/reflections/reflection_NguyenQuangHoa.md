# Reflection - NguyenQuangHoa

## Đóng góp kỹ thuật

- Thiết lập `.gitignore` để loại trừ API keys, cache, và các file generated không cần commit.
- Tổng hợp và kiểm tra `reports/benchmark_results.json` và `reports/summary.json` sau mỗi run.
- Định nghĩa contract giữa các module: `retrieved_ids` là interface chính giữa agent, retrieval evaluator và judge.
- Kiểm tra toàn bộ pipeline end-to-end: từ `synthetic_gen.py` đến `check_lab.py`.
- Review và đảm bảo các module kết nối đúng interface, phát hiện type mismatch (`retrieved_ids` string vs list).

## Quyết định kỹ thuật

- Giữ fallback deterministic/local để project vẫn chạy được khi thiếu API key hoặc provider timeout.
- Không commit `reports/` vào main để tránh conflict khi nhiều người chạy benchmark song song.
- Dùng 2 judge model slots qua OpenRouter để đáp ứng yêu cầu multi-judge consensus.
- Chuẩn hoá schema `retrieved_ids` ở tầng contract thay vì normalize riêng lẻ trong từng module.

## Vấn đề gặp phải

- OpenRouter/API calls làm benchmark chậm khi agent và judge đều gọi API cho 50 cases x 2 phiên bản.
- Một số module trả `retrieved_ids` dạng string thay vì list, phải chuẩn hoá ở tầng runner.
- Baseline file không tồn tại ở lần chạy đầu tiên, cần handle gracefully trong regression delta.

## Bằng chứng kiểm thử

- `python main.py`: toàn bộ pipeline chạy end-to-end, sinh đủ `reports/summary.json` và `reports/benchmark_results.json`.
- `python check_lab.py`: pass định dạng bài nộp.
- Benchmark summary:
  - Total cases: 50
  - Pass/Fail: 38/12
  - Avg score: 3.46
  - Agreement rate: 0.80

## Cải tiến tiếp theo

- Chuẩn hoá schema `retrieved_ids` ở tất cả module để tránh normalize nhiều chỗ.
- Thêm `.gitkeep` trong `reports/` thay vì commit output files.
- Retry judge khi OpenRouter trả JSON lỗi trước khi fallback.
- Implement full position-bias check bằng cách đổi thứ tự response A/B.
