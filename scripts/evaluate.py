"""Run the eval set through the pipeline; report accuracy, latency and failures; fail CI below a threshold."""
import argparse
import json
import statistics
from pathlib import Path

from langfuse import get_client

from app import pipeline
from app.llm import build_providers
from app.rag import RuleStore

p = argparse.ArgumentParser()
p.add_argument("--data", default="data/eval.jsonl")
p.add_argument("--min-accuracy", type=float, default=0.85)
p.add_argument("--out", default="eval_results.md")
args = p.parse_args()

store, providers, langfuse = RuleStore(), build_providers(), get_client()
rows = [json.loads(line) for line in Path(args.data).read_text(encoding="utf-8").splitlines() if line.strip()]

cat_hits = urg_hits = 0
latencies, misses = [], []
for row in rows:
    res = pipeline.run(row["note"], store, providers)
    ok_cat = res.category.value == row["category"]
    ok_urg = res.urgency.value == row["urgency"]
    cat_hits += ok_cat
    urg_hits += ok_urg
    latencies.append(res.latency_ms)
    if not ok_cat:
        misses.append((row["note"], row["category"], res.category.value))

n = len(rows)
cat_acc, urg_acc = cat_hits / n, urg_hits / n
p50 = statistics.median(latencies)
p95 = sorted(latencies)[max(0, int(0.95 * n) - 1)]
report = [
    "| Metric | Value |", "| --- | --- |",
    f"| Notes evaluated | {n} |",
    f"| Category accuracy | {cat_acc:.1%} |",
    f"| Urgency accuracy | {urg_acc:.1%} |",
    f"| Median latency | {p50:.0f} ms |",
    f"| p95 latency | {p95:.0f} ms |",
    "", "Misclassified:", *[f"- `{note}`: expected {exp}, got {got}" for note, exp, got in misses],
]
Path(args.out).write_text("\n".join(report), encoding="utf-8")
print("\n".join(report))
langfuse.flush()  # make sure every trace reaches Langfuse before the script exits
if cat_acc < args.min_accuracy:
    raise SystemExit(f"category accuracy {cat_acc:.1%} is below {args.min_accuracy:.0%}")
