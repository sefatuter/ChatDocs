import psycopg2
import os
import numpy as np
from pgvector.psycopg2 import register_vector
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import config
embedding_model = GPT4AllEmbeddings()

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

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=[
        "\n\n",
        "\n",
        " ",
        ".",
        ",",
        "\u200b",  # Zero-width space
        "\uff0c",  # Fullwidth comma
        "\u3001",  # Ideographic comma
        "\uff0e",  # Fullwidth full stop
        "\u3002",  # Ideographic full stop
        "",
    ],
)

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

def sanitize_content(content):
    """Remove NUL (0x00) characters and other problematic bytes from content."""
    if isinstance(content, str):
        return content.replace('\x00', '')
    elif isinstance(content, bytes):
        return content.replace(b'\x00', b'').decode('utf-8', errors='replace')
    return content

def store_documents(documents):
    """Splits documents into chunks, generates embeddings, and stores them in PostgreSQL.
    Prevents duplicate uploads by checking if the content already exists.
    """
    all_splits = text_splitter.split_documents(documents)
    
    with conn.cursor() as cur:
        for doc in all_splits:
            heading = doc.metadata.get("source", "Unknown")
            content = sanitize_content(doc.page_content)
            
            # Check for duplicates
            cur.execute("SELECT 1 FROM structured_documents WHERE content = %s", (content,))
            if cur.fetchone() is not None:
                continue

            # Generate embedding
            embedding = np.array(embedding_model.embed_query(content)).tolist()

            # Insert into database
            cur.execute("""
                INSERT INTO structured_documents (heading, content, embedding)
                VALUES (%s, %s, %s)
            """, (heading, content, embedding))
    
        conn.commit()

def search_documents(query, top_n=5):
    """Search for relevant documents using pgvector"""
    query_embedding = np.array(embedding_model.embed_query(query)).tolist()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT heading, content, (embedding <=> %s::vector) AS similarity
            FROM structured_documents
            ORDER BY similarity ASC
            LIMIT %s;
        """, (query_embedding, top_n))

        return cur.fetchall()