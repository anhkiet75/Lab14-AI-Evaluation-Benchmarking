# Reflection - TienAnhKiet

## Đóng góp kỹ thuật

- Thiết kế hard cases theo `data/HARD_CASES_GUIDE.md`: adversarial, goal hijacking, out-of-context, ambiguous, conflicting information, multi-turn correction, latency-cost.
- Định nghĩa contract giữa các module: `retrieved_ids` là interface chính giữa agent, retrieval evaluator và judge.
- Tích hợp OpenRouter làm provider chung cho dataset generation, agent generation và multi-judge consensus với fallback local.
- Thiết lập `.gitignore` và kiểm tra toàn bộ pipeline end-to-end: từ `synthetic_gen.py` đến `check_lab.py`.
- Review và merge contribution của các thành viên, đảm bảo các module kết nối đúng interface.

## Quyết định kỹ thuật

- Giữ fallback deterministic/local để project vẫn chạy được khi thiếu API key hoặc provider timeout.
- Không dùng `golden_set.jsonl` làm knowledge base trực tiếp để tránh leak đáp án vào agent.
- Dùng `retrieved_ids` làm contract chính giữa agent và retrieval evaluator, không so sánh text trực tiếp.
- Dùng 2 judge model slots qua OpenRouter để đáp ứng yêu cầu multi-judge consensus.

## Vấn đề gặp phải

- OpenRouter/API calls có thể làm benchmark chậm nếu agent và judge đều gọi API cho 50 cases x 2 phiên bản.
- Dataset hard cases có expected answer đôi khi yêu cầu suy luận ngoài corpus, làm score generation thấp dù retrieval đúng.
- Một số module dùng type không nhất quán (`retrieved_ids` dạng string thay vì list), phải chuẩn hoá ở tầng contract.

## Bằng chứng kiểm thử

- `python main.py`: toàn bộ pipeline chạy end-to-end, sinh đủ reports.
- `python check_lab.py`: pass định dạng bài nộp.
- Benchmark summary:
  - Total cases: 50
  - Pass/Fail: 38/12
  - Avg score: 3.46
  - Agreement rate: 0.80
  - Multi-judge reliability: 50/50 cases used both configured OpenRouter judge models.

## Cải tiến tiếp theo

- Bổ sung corpus để expected answer của hard cases có bằng chứng rõ hơn.
- Chuẩn hoá schema `retrieved_ids` ở tất cả module để tránh normalize nhiều chỗ.
- Retry judge khi OpenRouter trả JSON lỗi trước khi fallback.
- Implement full position-bias check bằng cách đổi thứ tự response A/B.
