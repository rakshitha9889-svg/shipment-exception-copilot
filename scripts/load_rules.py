"""Embed the handling rules and load them into Qdrant. Run once, and again whenever rules change."""
import sys

from app.rag import RuleStore

path = sys.argv[1] if len(sys.argv) > 1 else "data/rules.jsonl"
print(f"loaded {RuleStore().load(path)} rules")
