import psycopg2
import numpy as np
from pgvector.psycopg2 import register_vector
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import PG_DATABASE, PG_USER, PG_PASSWORD, PG_HOST, PG_PORT

embedding_model = GPT4AllEmbeddings()

# DB connection
conn = psycopg2.connect(
    dbname=PG_DATABASE,
    user=PG_USER,
    password=PG_PASSWORD,
    host=PG_HOST,
    port=PG_PORT
)
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
    ],)

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
                    session_id VARCHAR(255) NOT NULL,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL
                );
            """)
        conn.commit()

create_table()

def store_documents(documents):
    """Splits documents into chunks, generates embeddings, and stores them in PostgreSQL.
    Prevents duplicate uploads by checking if the content already exists.
    """
    all_splits = text_splitter.split_documents(documents)
    
    with conn.cursor() as cur:
        for doc in all_splits:
            heading = doc.metadata.get("source", "Unknown")
            content = doc.page_content
            
            cur.execute("SELECT 1 FROM structured_documents WHERE content = %s", (content,))
            if cur.fetchone() is not None:
                continue

            embedding = np.array(embedding_model.embed_query(content)).tolist()

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

