import os

PG_DATABASE = os.getenv("PG_DATABASE", "pgllm")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "psql1234")
PG_HOST = os.getenv("PG_HOST", "postgres")
PG_PORT = os.getenv("PG_PORT", 5432)

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://ollama:11434")
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:1.5b"

EMBEDDING_DIM = 384
