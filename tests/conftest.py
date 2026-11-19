import os

# Tests never call a real LLM or Langfuse.
os.environ.setdefault("LANGFUSE_TRACING_ENABLED", "false")
os.environ.setdefault("LLM_API_KEY", "test-key")
