"""Generate synthetic courier notes with the LLM, using the reviewed seed notes as examples.

Usage: python -m scripts.generate_notes --per-category 40
Writes data/notes.jsonl. `generated_for` is the category the note was ASKED for, not a checked label.
"""
import argparse
import json
import random
import time
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel

from app.config import settings
from app.schemas import Category

PROMPT = """You write realistic courier exception notes for a German parcel network.
Couriers type them fast on a handheld scanner: short, abbreviations (Pkt, Empf., Hausnr, pkg, rcpt),
typos, missing words, sometimes mixed German and English.

Examples of real-style notes:
{examples}

Write {n} NEW notes for the category "{category}".
Language mix: about 45% German, 35% English, 20% mixed German/English.
Length 3 to 25 words. Vary the situation, place names and wording; do not copy the examples.
Include a few hard cases that a reader could confuse with another category."""


class NoteBatch(BaseModel):
    notes: list[str]


def norm(text: str) -> str:
    return " ".join(text.lower().split())


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", default="data/seed_notes.jsonl")
    p.add_argument("--out", default="data/notes.jsonl")
    p.add_argument("--per-category", type=int, default=40)
    p.add_argument("--pause", type=float, default=5.0, help="seconds between calls (free-tier rate limits)")
    args = p.parse_args()

    seeds = [json.loads(line) for line in Path(args.seeds).read_text(encoding="utf-8").splitlines() if line.strip()]
    seen = {norm(s["note"]) for s in seeds}
    client = OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key, timeout=120)
    rng = random.Random(42)  # fixed seed: the same examples are picked on every run

    rows = []
    for cat in Category:
        same = [s["note"] for s in seeds if s["category"] == cat.value]
        others = [s["note"] for s in seeds if s["category"] != cat.value]
        examples = "\n".join(f"- {n}" for n in same + rng.sample(others, min(4, len(others))))
        resp = client.chat.completions.parse(
            model=settings.llm_model,
            messages=[{"role": "user", "content": PROMPT.format(examples=examples, n=args.per_category,
                                                                 category=cat.value)}],
            response_format=NoteBatch,
            temperature=1.0,
        )
        batch = resp.choices[0].message.parsed.notes if resp.choices[0].message.parsed else []
        kept = 0
        for note in batch:
            key = norm(note)
            if len(note.split()) < 3 or key in seen:
                continue  # drop too-short notes and duplicates of seeds or earlier notes
            seen.add(key)
            rows.append({"note": note.strip(), "generated_for": cat.value})
            kept += 1
        print(f"{cat.value:<17} asked {args.per_category}, got {len(batch)}, kept {kept}")
        time.sleep(args.pause)

    rng.shuffle(rows)
    with Path(args.out).open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} notes to {args.out}")


if __name__ == "__main__":
    main()
