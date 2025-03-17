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

DEFAULT_DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "user": "postgres",
    "password": "psql1234",
}

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "your-api-key") # Enter with your email https://build.nvidia.com/explore/discover and get free 1000 api calls.
