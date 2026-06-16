# Reflection - NguyenQuangHoa

## Đóng góp kỹ thuật

- Thiết kế và xây dựng toàn bộ `data/synthetic_gen.py` để sinh 50 test cases tổng hợp với đa dạng chủ đề.
- Định nghĩa schema cho `golden_set.jsonl`: `question`, `expected_answer`, `expected_retrieval_ids`, `difficulty`, `source_doc_id`.
- Phân loại dataset theo 4 mức độ: easy, medium, hard, adversarial — đảm bảo phân phối đều 15/15/12/8.
- Viết hàm kiểm tra tính nhất quán giữa `expected_retrieval_ids` và corpus documents trong knowledge base.
- Tích hợp OpenRouter để sinh câu hỏi đa dạng, fallback sang template-based generation khi thiếu API key.

## Quyết định kỹ thuật

- Tách biệt corpus khỏi golden set để tránh data leakage vào agent generation.
- Dùng seed cố định khi gọi LLM để đảm bảo reproducibility của dataset.
- Lưu `source_doc_id` trong mỗi test case để phục vụ retrieval evaluation sau này.
- Chọn jsonl thay vì json array để dễ append và stream khi dataset lớn.

## Vấn đề gặp phải

- Một số câu hỏi được sinh ra quá giống nhau (near-duplicate), cần thêm bước deduplication.
- Hard cases với conflicting information đôi khi không có `expected_retrieval_ids` rõ ràng.
- OpenRouter rate limit khi sinh dataset lớn, phải thêm exponential backoff.

## Bằng chứng kiểm thử

- `python data/synthetic_gen.py`: tạo đủ 50 test cases, phân phối difficulty đều.
- `python check_lab.py`: pass kiểm tra format dataset.
- Dataset stats: 15 easy, 15 medium, 12 hard, 8 adversarial cases.
- Tất cả cases có đủ field bắt buộc: `id`, `question`, `expected_answer`, `expected_retrieval_ids`.

## Cải tiến tiếp theo

- Thêm bước deduplication tự động dùng embedding similarity.
- Mở rộng dataset lên 100 cases với thêm multi-hop reasoning questions.
- Thêm metadata về nguồn gốc câu hỏi để phân tích lỗi theo category.
- Tích hợp human review pipeline để validate chất lượng expected answers.
