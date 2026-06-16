import asyncio
import json
import os
import time
from engine.runner import BenchmarkRunner
from engine.retrieval_eval import RetrievalEvaluator
from engine.llm_judge import LLMJudge
from agent.main_agent import MainAgent

RELEASE_THRESHOLDS = {
    "min_avg_score": 3.0,
    "min_hit_rate": 0.8,
    "min_mrr": 0.7,
    "min_agreement_rate": 0.6,
    "max_avg_latency": 2.0,
    "max_score_regression": -0.1,
}

async def run_benchmark_with_results(agent_version: str):
    print(f"🚀 Khởi động Benchmark cho {agent_version}...")

    if not os.path.exists("data/golden_set.jsonl"):
        print("❌ Thiếu data/golden_set.jsonl. Hãy chạy 'python data/synthetic_gen.py' trước.")
        return None, None

    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if not dataset:
        print("❌ File data/golden_set.jsonl rỗng. Hãy tạo ít nhất 1 test case.")
        return None, None

    runner = BenchmarkRunner(MainAgent(), RetrievalEvaluator(), LLMJudge())
    results = await runner.run_all(dataset)

    total = len(results)
    avg_score = sum(r["judge"]["final_score"] for r in results) / total
    hit_rate = sum(r["ragas"]["retrieval"]["hit_rate"] for r in results) / total
    mrr = sum(r["ragas"]["retrieval"]["mrr"] for r in results) / total
    agreement_rate = sum(r["judge"]["agreement_rate"] for r in results) / total
    avg_latency = sum(r["latency"] for r in results) / total
    total_tokens = sum(r["agent_metadata"].get("tokens_used", 0) for r in results)
    estimated_cost = sum(r["agent_metadata"].get("cost_usd", 0.0) for r in results)
    pass_count = sum(1 for r in results if r["status"] == "pass")
    summary = {
        "metadata": {
            "version": agent_version,
            "total": total,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "pass_count": pass_count,
            "fail_count": total - pass_count,
        },
        "metrics": {
            "avg_score": avg_score,
            "hit_rate": hit_rate,
            "mrr": mrr,
            "agreement_rate": agreement_rate,
            "avg_latency": avg_latency,
            "total_tokens": total_tokens,
            "estimated_cost": round(estimated_cost, 6),
        },
    }
    return results, summary

async def run_benchmark(version):
    _, summary = await run_benchmark_with_results(version)
    return summary

async def main():
    v1_summary = await run_benchmark("Agent_V1_Base")
    
    # Giả lập V2 có cải tiến (để test logic)
    v2_results, v2_summary = await run_benchmark_with_results("Agent_V2_Optimized")
    
    if not v1_summary or not v2_summary:
        print("❌ Không thể chạy Benchmark. Kiểm tra lại data/golden_set.jsonl.")
        return

    print("\n📊 --- KẾT QUẢ SO SÁNH (REGRESSION) ---")
    delta = v2_summary["metrics"]["avg_score"] - v1_summary["metrics"]["avg_score"]
    print(f"V1 Score: {v1_summary['metrics']['avg_score']}")
    print(f"V2 Score: {v2_summary['metrics']['avg_score']}")
    print(f"Delta: {'+' if delta >= 0 else ''}{delta:.2f}")

    release_decision = evaluate_release_gate(v1_summary, v2_summary)
    v2_summary["regression"] = {
        "baseline_version": v1_summary["metadata"]["version"],
        "candidate_version": v2_summary["metadata"]["version"],
        "score_delta": delta,
    }
    v2_summary["release_gate"] = release_decision

    os.makedirs("reports", exist_ok=True)
    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(v2_summary, f, ensure_ascii=False, indent=2)
    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(v2_results, f, ensure_ascii=False, indent=2)

    if release_decision["decision"] == "approve":
        print("✅ QUYẾT ĐỊNH: CHẤP NHẬN BẢN CẬP NHẬT (APPROVE)")
    else:
        print("❌ QUYẾT ĐỊNH: TỪ CHỐI (BLOCK RELEASE)")

def evaluate_release_gate(v1_summary, v2_summary):
    metrics = v2_summary["metrics"]
    score_delta = metrics["avg_score"] - v1_summary["metrics"]["avg_score"]
    checks = {
        "avg_score": metrics["avg_score"] >= RELEASE_THRESHOLDS["min_avg_score"],
        "hit_rate": metrics["hit_rate"] >= RELEASE_THRESHOLDS["min_hit_rate"],
        "mrr": metrics["mrr"] >= RELEASE_THRESHOLDS["min_mrr"],
        "agreement_rate": metrics["agreement_rate"] >= RELEASE_THRESHOLDS["min_agreement_rate"],
        "avg_latency": metrics["avg_latency"] <= RELEASE_THRESHOLDS["max_avg_latency"],
        "score_regression": score_delta >= RELEASE_THRESHOLDS["max_score_regression"],
    }
    return {
        "decision": "approve" if all(checks.values()) else "block",
        "checks": checks,
        "thresholds": RELEASE_THRESHOLDS,
    }

if __name__ == "__main__":
    asyncio.run(main())
