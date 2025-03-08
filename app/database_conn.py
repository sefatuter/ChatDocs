import psycopg2
import os
import numpy as np
from pgvector.psycopg2 import register_vector
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import config

# DB connection
conn = psycopg2.connect(
    dbname=config.PG_DATABASE,
    user=config.PG_USER,
    password=config.PG_PASSWORD,
    host=config.PG_HOST,
    port=config.PG_PORT
)

with conn.cursor() as cur:
    cur.execute("COMMIT; CREATE EXTENSION IF NOT EXISTS vector;")
    conn.commit()
    
register_vector(conn)

def create_table():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE EXTENSION IF NOT EXISTS vector;
            CREATE TABLE IF NOT EXISTS structured_documents (
                id SERIAL PRIMARY KEY,
                heading TEXT,
                content TEXT,
                embedding VECTOR(384)
            );
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                role TEXT NOT NULL,
                message TEXT NOT NULL
            );
        """)
        conn.commit()
create_table()