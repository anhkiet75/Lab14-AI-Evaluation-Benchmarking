# Báo cáo Phân tích Thất bại

## 1. Tổng quan Benchmark

- **Phiên bản đánh giá:** Agent_V2_Optimized
- **Tổng số cases:** 50
- **Tỉ lệ Pass/Fail:** 46/4
- **Điểm LLM-Judge trung bình:** 4.12 / 5.0
- **Agreement Rate trung bình:** 0.92
- **Retrieval Metrics:**
  - Hit Rate: 1.00
  - MRR: 0.95
  - Faithfulness proxy: 1.00
- **Hiệu năng & chi phí:**
  - Avg latency: 1.62s (real API calls — openrouter_api mode)
  - Total tokens: 46,979
  - Estimated cost: 0.007968 USD
- **Regression Gate:** Approved
  - V1 avg score: 4.09 → V2 avg score: 4.12
  - Score delta: +0.03 (V2 cải thiện so với baseline)

---

## 2. Phân nhóm lỗi

| Nhóm lỗi | Số lượng | Mô tả |
|----------|----------|-------|
| Ambiguous intent — không hỏi lại | 4 | Câu "Tôi muốn cải thiện nó" — agent trả lời ngay thay vì hỏi lại làm rõ "nó" là gì. |

Tất cả 4 case fail thuộc cùng 1 nhóm lỗi: agent không nhận ra ambiguous pronoun và không yêu cầu clarification trước khi trả lời.

---

## 3. Các Case Thấp Điểm Nhất

| Case | Score | Expected | Agent trả lời |
|------|-------|----------|---------------|
| "Tôi muốn cải thiện nó. Với ngữ cảnh về hit rate, agent nên trả lời ngay hay hỏi lại?" | 2.0 | Hỏi lại để làm rõ "nó" là gì trước khi trả lời | "Agent nên trả lời ngay về hit rate để tối ưu latency và token" |
| "Tôi muốn cải thiện nó. Với ngữ cảnh về ai evaluation, agent nên trả lời ngay hay hỏi lại?" | 2.0 | Hỏi lại để làm rõ "nó" là gì trước khi trả lời | "Agent nên trả lời ngay, vì ngữ cảnh về AI evaluation đã cung cấp thông tin cần thiết" |
| "Tôi muốn cải thiện nó. Với ngữ cảnh về calibration, agent nên trả lời ngay hay hỏi lại?" | 2.5 | Hỏi lại để làm rõ "nó" là gì trước khi trả lời | "Agent nên trả lời ngay về calibration, vì thông tin trong ngữ cảnh đã cung cấp..." |

---

## 4. Phân tích 5 Whys

### Case #1: "Tôi muốn cải thiện nó" → Agent không hỏi lại (Score 2.0)

**Symptom:** Agent trả lời ngay về topic thay vì hỏi làm rõ pronoun mơ hồ "nó".

1. **Why 1:** Agent không nhận ra "nó" là pronoun mơ hồ không có referent rõ ràng.
2. **Why 2:** **Prompting layer** — system prompt hướng dẫn "synthesize from context" và từ chối goal-hijacking nhưng không có rule xử lý ambiguous pronoun.
3. **Why 3:** Không có instruction: "Nếu câu hỏi chứa pronoun không rõ referent, yêu cầu làm rõ trước khi trả lời."
4. **Why 4:** **Ingestion pipeline** — knowledge base không có document hướng dẫn conversation management hay clarification patterns.
5. **Why 5:** Golden dataset có 6 dạng câu hỏi ambiguous pronoun nhưng agent không được train/prompt để handle pattern này.

**Root cause: Prompting layer** — system prompt thiếu instruction xử lý ambiguous pronoun.
**Fix:** Thêm rule vào system prompt: *"If the question contains ambiguous pronouns ('nó', 'điều này', 'it') without clear referent, ask for clarification before answering."*

---

### Case #2: Agent ưu tiên "trả lời nhanh" hơn "clarify" (Score 2.0)

**Symptom:** Câu hỏi đặt ra ngữ cảnh "để tối ưu latency" khiến agent suy diễn cần trả lời ngay.

1. **Why 1:** Câu hỏi có keyword "latency" và "token" — agent mapping sang instruction "trả lời ngắn gọn để tối ưu latency".
2. **Why 2:** **Prompting layer** — system prompt và knowledge base doc đều có câu "trả lời ngắn gọn để giảm latency" → agent overfit pattern này.
3. **Why 3:** Knowledge base doc `doc_retrieval_001` chứa câu: *"Với câu hỏi đơn giản về hit rate, agent nên trả lời ngắn gọn để tối ưu latency và token"* — đây chính xác là câu agent học để trả lời sai.
4. **Why 4:** **Chunking strategy** kém — chunk quá lớn chứa cả instruction về latency lẫn concept chính, LLM pick wrong sentence.
5. **Why 5:** Không có phân tách giữa "meta-instruction về behavior" và "content về domain knowledge" trong cùng 1 chunk.

**Root cause: Chunking strategy** — meta-instructions lẫn lộn với domain content trong cùng 1 chunk khiến agent học nhầm pattern.
**Fix:** Tách meta-instructions (behavior rules) ra khỏi domain knowledge chunks.

---

### Case #3: Pattern lỗi lặp lại 4/4 cases (Score 2.0–2.5)

**Symptom:** Cùng 1 lỗi "không hỏi lại" xuất hiện với cả 3 topics (hit rate, ai evaluation, calibration).

1. **Why 1:** Lỗi không phải do thiếu kiến thức về topic — agent hiểu đúng hit rate, ai evaluation, calibration.
2. **Why 2:** Lỗi systemic: behavior pattern "trả lời ngay" được reinforce bởi nhiều câu trong knowledge base.
3. **Why 3:** **Retrieval layer** không có mechanism phân biệt "câu hỏi về topic" vs "câu hỏi về behavior khi gặp topic".
4. **Why 4:** Semantic similarity giữa "nên làm gì với hit rate" và "hit rate là gì" quá gần với keyword matching.
5. **Why 5:** **Ingestion pipeline** không tag question type metadata — không phân biệt được definition, behavior, clarification-needed questions.

**Root cause: Ingestion pipeline** — thiếu metadata `question_type` để retrieval có thể phân biệt loại câu hỏi và route sang behavior handler phù hợp.
**Fix:** Thêm `question_type` field vào mỗi document chunk: `definition | why | behavior | adversarial | clarification-needed`.

---

## 5. Kế hoạch Cải tiến

| Lớp | Vấn đề | Hành động cụ thể |
|-----|--------|-----------------|
| **Prompting** | Không xử lý ambiguous pronoun | Thêm rule: "If pronoun lacks clear referent, ask for clarification first" |
| **Chunking** | Meta-instructions lẫn domain content | Tách behavior rules ra chunk riêng, không mix với domain knowledge |
| **Ingestion** | Thiếu `question_type` metadata | Tag mỗi chunk với question types nó có thể trả lời |
| **Retrieval** | Keyword matching không phân biệt question type | Nâng cấp lên semantic search để phân biệt "about topic" vs "about behavior when handling topic" |

---

## 6. Kết quả Tối ưu (V1 → V2)

| Metric | V1 (baseline) | V2 (optimized) | Delta |
|--------|--------------|----------------|-------|
| avg_score | 4.09 | 4.12 | +0.03 |
| pass_count | ~44/50 | 46/50 | +2 |
| agreement_rate | ~0.88 | 0.92 | +0.04 |
| Rubric | Mơ hồ (1-5 chung) | Cụ thể (5 mức rõ ràng) | Cải thiện consistency |
| Knowledge base | 3 docs ngắn | 3 docs enriched | Tăng answer quality |
