from typing import List, Dict

class RetrievalEvaluator:
    def __init__(self):
        self.default_top_k = 3

    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        """
        TODO: Tính toán xem ít nhất 1 trong expected_ids có nằm trong top_k của retrieved_ids không.
        """
        if not expected_ids or not retrieved_ids:
            return 0.0

        top_retrieved = retrieved_ids[:top_k]
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        """
        TODO: Tính Mean Reciprocal Rank.
        Tìm vị trí đầu tiên của một expected_id trong retrieved_ids.
        MRR = 1 / position (vị trí 1-indexed). Nếu không thấy thì là 0.
        """
        if not expected_ids or not retrieved_ids:
            return 0.0

        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)
        return 0.0

    async def score(self, test_case: Dict, agent_response: Dict) -> Dict:
        """
        Calculate retrieval metrics for one benchmark case.

        BenchmarkRunner expects this method and stores the result under the
        `ragas` key, so the return shape keeps `retrieval.hit_rate` and
        `retrieval.mrr` stable for downstream summary code.
        """
        expected_ids = test_case.get("expected_retrieval_ids", [])
        retrieved_ids = agent_response.get("retrieved_ids", [])
        contexts = agent_response.get("contexts", [])

        hit_rate = self.calculate_hit_rate(expected_ids, retrieved_ids, self.default_top_k)
        mrr = self.calculate_mrr(expected_ids, retrieved_ids)
        relevancy = 1.0 if contexts else 0.0

        return {
            "faithfulness": hit_rate,
            "relevancy": relevancy,
            "retrieval": {
                "hit_rate": hit_rate,
                "mrr": mrr,
                "expected_ids": expected_ids,
                "retrieved_ids": retrieved_ids,
                "top_k": self.default_top_k,
            },
        }

    async def evaluate_batch(self, dataset: List[Dict]) -> Dict:
        """
        Chạy eval cho toàn bộ bộ dữ liệu.
        Dataset cần có trường 'expected_retrieval_ids' và Agent trả về 'retrieved_ids'.
        """
        if not dataset:
            return {"avg_hit_rate": 0.0, "avg_mrr": 0.0, "total": 0}

        hit_rates = []
        mrr_scores = []

        for item in dataset:
            expected_ids = item.get("expected_retrieval_ids", [])
            retrieved_ids = item.get("retrieved_ids", [])
            hit_rates.append(self.calculate_hit_rate(expected_ids, retrieved_ids, self.default_top_k))
            mrr_scores.append(self.calculate_mrr(expected_ids, retrieved_ids))

        total = len(dataset)
        return {
            "avg_hit_rate": sum(hit_rates) / total,
            "avg_mrr": sum(mrr_scores) / total,
            "total": total,
        }
