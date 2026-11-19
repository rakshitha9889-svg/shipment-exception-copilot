"""Nightly batch inference: classify every note in an input file, write results as JSON lines."""
import json
import sys
from pathlib import Path

from langfuse import get_client

from app import pipeline
from app.llm import AllProvidersFailed, build_providers
from app.rag import RuleStore

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
store, providers = RuleStore(), build_providers()
done = failed = 0
with dst.open("w", encoding="utf-8") as out:
    for line in src.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        note = json.loads(line)["note"]
        try:
            res = pipeline.run(note, store, providers)
            out.write(json.dumps({"note": note, **res.model_dump(mode="json")}, ensure_ascii=False) + "\n")
            done += 1
        except AllProvidersFailed as e:
            out.write(json.dumps({"note": note, "error": str(e)}, ensure_ascii=False) + "\n")
            failed += 1
get_client().flush()
print(f"classified {done}, failed {failed}")
sys.exit(1 if failed and not done else 0)
