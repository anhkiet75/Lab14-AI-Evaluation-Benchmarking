# Reflection - NguyenTuanMinh

## Đóng góp kỹ thuật

- Xây dựng `engine/llm_judge.py` với hai judge strategy: `strict` và `lenient` để so sánh đánh giá.
- Implement multi-judge consensus: lấy trung bình score và tính agreement rate giữa các judge.
- Thiết kế prompt template cho judge với rubric rõ ràng: relevance, factuality, completeness (thang 1–5).
- Xử lý JSON parse failures từ LLM judge bằng regex fallback để extract score từ raw text.
- Cấu hình hai model slots qua OpenRouter để đảm bảo independent judgment.

## Quyết định kỹ thuật

- Dùng temperature=0 cho judge calls để đảm bảo determinism trong scoring.
- Thiết kế judge prompt theo dạng chain-of-thought: judge giải thích trước, cho điểm sau.
- Agreement rate threshold 0.7 được chọn là mức tối thiểu để kết quả đáng tin cậy.
- Fallback heuristic score = 3 (trung bình) khi cả hai parse strategy đều thất bại.

## Vấn đề gặp phải

- Một số model OpenRouter trả markdown code block thay vì raw JSON, cần strip trước khi parse.
- Position bias: judge đôi khi favors câu trả lời ngắn hơn bất kể chất lượng.
- Timeout khi judge 50 cases x 2 models, cần implement concurrent calls với semaphore.

## Bằng chứng kiểm thử

- `python main.py`: multi-judge chạy đủ 50/50 cases với cả 2 configured models.
- Agreement rate: 0.80 (trên threshold 0.70).
- Avg score: 3.46/5.0 trên toàn bộ test suite.
- Pass/Fail: 38/12 cases (threshold score ≥ 3.0).

## Cải tiến tiếp theo

- Implement position-bias mitigation: swap A/B order và average kết quả.
- Retry với exponential backoff trước khi fallback về heuristic score.
- Thêm calibration step: human-labeled subset để căn chỉnh judge score.
- Cache judge results để tránh gọi API lại khi re-run benchmark cùng dataset.
