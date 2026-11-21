"""Pick a balanced sample of generated notes for hand-labeling, or check a finished eval file.

  python -m scripts.make_eval_set            # writes data/eval.jsonl (labels pre-filled, urgency blank)
  python -m scripts.make_eval_set --check    # validates data/eval.jsonl after you have labeled it
"""
import argparse
import collections
import json
import random
from pathlib import Path

from app.schemas import Category, Urgency

CATS = {c.value for c in Category}
URGS = {u.value for u in Urgency}


def make(src: Path, dst: Path, per_category: int) -> None:
    if dst.exists():
        raise SystemExit(f"{dst} already exists; not overwriting your labels")
    rows = [json.loads(line) for line in src.read_text(encoding="utf-8").splitlines() if line.strip()]
    rng = random.Random(7)
    by_cat = collections.defaultdict(list)
    for r in rows:
        by_cat[r["generated_for"]].append(r)
    picked = []
    for cat in sorted(by_cat):
        picked += rng.sample(by_cat[cat], min(per_category, len(by_cat[cat])))
    rng.shuffle(picked)  # mixed order, so you judge each note on its own
    with dst.open("w", encoding="utf-8") as f:
        for r in picked:
            f.write(json.dumps({"note": r["note"], "category": r["generated_for"], "urgency": ""},
                               ensure_ascii=False) + "\n")
    print(f"wrote {len(picked)} notes to {dst}; now correct EVERY category and fill in EVERY urgency")


def check(dst: Path) -> None:
    problems, cats, urgs = [], collections.Counter(), collections.Counter()
    for i, line in enumerate(dst.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError as e:
            problems.append(f"line {i}: not valid JSON ({e.msg})")
            continue
        if r.get("category") not in CATS:
            problems.append(f"line {i}: category {r.get('category')!r} is not one of {sorted(CATS)}")
        if r.get("urgency") not in URGS:
            problems.append(f"line {i}: urgency {r.get('urgency')!r} must be low, medium or high")
        cats[r.get("category")] += 1
        urgs[r.get("urgency")] += 1
    print("categories:", dict(sorted(cats.items(), key=lambda kv: str(kv[0]))))
    print("urgency:   ", dict(urgs))
    if problems:
        print(f"{len(problems)} problems, first 10:")
        print("\n".join(problems[:10]))
    else:
        print(f"OK: {sum(cats.values())} labeled notes")
    thin = [c for c in CATS if cats[c] < 10]
    if thin:
        print("fewer than 10 notes for:", ", ".join(sorted(thin)))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--src", default="data/notes.jsonl")
    p.add_argument("--out", default="data/eval.jsonl")
    p.add_argument("--per-category", type=int, default=15)
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    check(Path(a.out)) if a.check else make(Path(a.src), Path(a.out), a.per_category)
