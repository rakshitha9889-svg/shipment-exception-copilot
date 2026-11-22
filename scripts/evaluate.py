"""Run the eval set through the pipeline; report accuracy, latency and failures; fail CI below a threshold."""
import argparse
import collections
import json
import statistics
import time
from pathlib import Path

from langfuse import get_client

from app import pipeline
from app.llm import AllProvidersFailed, build_providers
from app.rag import RuleStore

p = argparse.ArgumentParser()
p.add_argument("--data", default="data/eval.jsonl")
p.add_argument("--min-accuracy", type=float, default=0.85)
p.add_argument("--out", default="eval_results.md")
p.add_argument("--pause", type=float, default=4.0, help="seconds between notes (free-tier rate limits)")
args = p.parse_args()

store, providers, langfuse = RuleStore(), build_providers(), get_client()
rows = [json.loads(line) for line in Path(args.data).read_text(encoding="utf-8").splitlines() if line.strip()]

cat_hits = urg_hits = 0
latencies, misses, failed = [], [], []
urg_misses, urg_confusion = [], collections.Counter()
for i, row in enumerate(rows, 1):
    try:
        res = pipeline.run(row["note"], store, providers)
    except AllProvidersFailed as e:
        failed.append(row["note"])  # counted as wrong, listed in the report
        print(f"[{i}/{len(rows)}] FAILED: {e}")
        continue
    finally:
        time.sleep(args.pause)
    print(f"[{i}/{len(rows)}] {res.category.value} ({res.latency_ms:.0f} ms)")
    ok_cat = res.category.value == row["category"]
    ok_urg = res.urgency.value == row["urgency"]
    cat_hits += ok_cat
    urg_hits += ok_urg
    latencies.append(res.latency_ms)
    if not ok_cat:
        misses.append((row["note"], row["category"], res.category.value))
    if not ok_urg:
        urg_misses.append((row["note"], row["urgency"], res.urgency.value))
        urg_confusion[(row["urgency"], res.urgency.value)] += 1

n = len(rows)
cat_acc, urg_acc = cat_hits / n, urg_hits / n
p50 = statistics.median(latencies) if latencies else 0
p95 = sorted(latencies)[max(0, int(0.95 * len(latencies)) - 1)] if latencies else 0
report = [
    "| Metric | Value |", "| --- | --- |",
    f"| Notes evaluated | {n} |",
    f"| Category accuracy | {cat_acc:.1%} |",
    f"| Urgency accuracy | {urg_acc:.1%} |",
    f"| Median latency | {p50:.0f} ms |",
    f"| p95 latency | {p95:.0f} ms |",
    f"| Failed calls | {len(failed)} |",
    "", "Misclassified:", *[f"- `{note}`: expected {exp}, got {got}" for note, exp, got in misses],
    "", "Failed:", *[f"- `{note}`" for note in failed],
    "", "Urgency errors (expected -> got: count):",
    *[f"- {exp} -> {got}: {c}" for (exp, got), c in urg_confusion.most_common()],
    "", "Urgency misclassified:", *[f"- `{note}`: expected {exp}, got {got}" for note, exp, got in urg_misses],
]
Path(args.out).write_text("\n".join(report), encoding="utf-8")
print("\n".join(report))
langfuse.flush()  # make sure every trace reaches Langfuse before the script exits
if cat_acc < args.min_accuracy:
    raise SystemExit(f"category accuracy {cat_acc:.1%} is below {args.min_accuracy:.0%}")
