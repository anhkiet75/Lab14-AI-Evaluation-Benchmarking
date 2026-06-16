# Reflection - VuDinhPhuong

## Đóng góp kỹ thuật

- Xây dựng toàn bộ `agent/main_agent.py` theo RAG pattern: retrieve context → build grounded prompt → generate answer.
- Đảm bảo agent response object trả về đúng contract: `contexts`, `retrieved_ids`, `token_count`, `cost_estimate`.
- Viết `.env.example` với đầy đủ biến môi trường cho OpenRouter và local fallback.
- Viết `analysis/failure_analysis.md`: phân tích 12 failed cases theo pattern (hallucination, off-topic, incomplete).
- Phân loại failure modes: retrieval miss (3 cases), generation drift (5 cases), judge disagreement (4 cases).

## Quyết định kỹ thuật

- Agent không dùng `golden_set.jsonl` làm knowledge base để tránh leak expected answers.
- Giữ fallback deterministic/local để hệ thống chạy được khi thiếu API key.
- System prompt được thiết kế để enforce grounding: agent phải trích dẫn từ retrieved contexts, không được dùng prior knowledge.
- Tách `contexts` (raw text) và `retrieved_ids` (doc identifiers) theo đúng contract đã thống nhất với team.

## Vấn đề gặp phải

- Agent đôi khi ignore retrieved context và trả lời từ prior knowledge, gây hallucination.
- 5 generation drift cases: agent trả lời đúng chủ đề nhưng thêm thông tin không có trong corpus.
- Judge disagreement cases: một judge cho 4/5, judge kia cho 2/5 cho cùng câu trả lời.

## Bằng chứng kiểm thử

- `python main.py`: agent chạy đầy đủ 50 cases, mỗi response có đủ fields theo contract.
- Failure analysis xác định được 3 failure categories rõ ràng với root cause.
- `.env.example` đã verify bằng cách chạy thử với API key thật.
- `python check_lab.py`: pass toàn bộ format checks.

## Cải tiến tiếp theo

- Thêm grounding check trong agent: verify mỗi claim có citation rõ ràng từ retrieved context.
- Phân tích 4 judge disagreement cases để xác định nguyên nhân: ambiguous rubric hay borderline answers.
- Thêm intent classification trước generation để xử lý adversarial inputs tốt hơn.
- Document failure patterns vào `data/HARD_CASES_GUIDE.md` để cải thiện dataset thế hệ sau.
