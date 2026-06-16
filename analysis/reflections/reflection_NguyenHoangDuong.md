# Reflection - NguyenHoangDuong

## Đóng góp kỹ thuật

- Hoàn thiện `engine/retrieval_eval.py`: tính Hit Rate và MRR theo từng case và toàn batch.
- Implement `RetrievalEvaluator` class với phương thức `evaluate_batch()` và `evaluate_single()`.
- Xử lý edge cases: `retrieved_ids` rỗng, `expected_retrieval_ids` null, partial match.
- Thêm per-case metrics vào benchmark report để phân tích retrieval failure patterns.
- Viết unit tests cho `RetrievalEvaluator` với mock retrieved_ids.

## Quyết định kỹ thuật

- Dùng `retrieved_ids` làm contract chính giữa agent và evaluator thay vì so sánh text.
- MRR tính trên vị trí đầu tiên của relevant doc trong ranked list, không average across relevant docs.
- Hit Rate@K với K=3 mặc định, configurable qua constructor.
- Trả về 0.0 thay vì raise exception khi `retrieved_ids` rỗng để không block toàn batch.

## Vấn đề gặp phải

- Agent đôi khi trả `retrieved_ids` dạng string thay vì list, cần normalize input.
- Hard cases với nhiều relevant docs: Hit Rate@1 thấp dù @3 cao, cần cả hai metrics.
- Một số expected_retrieval_ids trong dataset trỏ đến doc không có trong corpus.

## Bằng chứng kiểm thử

- Unit tests cho `RetrievalEvaluator`: 100% pass với edge cases.
- Integration test với full pipeline:
  - Hit Rate: 1.0
  - MRR: 1.0
- Per-case metrics được ghi đầy đủ vào `benchmark_results.json`.

## Cải tiến tiếp theo

- Thêm NDCG metric để đánh giá ranked retrieval quality tốt hơn.
- Phân tích failure cases: tìm pattern trong những case có Hit Rate = 0.
- Thêm Hit Rate@1, @3, @5 cùng lúc thay vì chỉ một K.
- Visualize retrieval performance theo difficulty level của dataset.
