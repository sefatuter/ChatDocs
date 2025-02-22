## Setup Postgres Database
```
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql.service
sudo -u postgres psql

postgres=# ALTER USER postgres WITH PASSWORD 'psql1234';
postgres=# CREATE DATABASE pgllm;
postgres=# \c pgllm
pgllm=# CREATE TABLE structured_documents (
    id SERIAL PRIMARY KEY,
    heading TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1024),
    search_tsv TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', heading), 'A') || 
        setweight(to_tsvector('english', content), 'B')
    ) STORED
);

pgllm=# CREATE EXTENSION IF NOT EXISTS vector;
```





## Setting Up Environment
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Ollama Installation
```
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3:instruct
ollama pull bge-m3:latest
ollama serve
```