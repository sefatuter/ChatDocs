import psycopg2
from psycopg2.pool import ThreadedConnectionPool
import os
import numpy as np
from pgvector.psycopg2 import register_vector
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import config

# DB connection
pool = ThreadedConnectionPool(1, 20,
    dbname=config.PG_DATABASE,
    user=config.PG_USER,
    password=config.PG_PASSWORD,
    host=config.PG_HOST,
    port=config.PG_PORT
)

conn = pool.getconn()

with conn.cursor() as cur:
    cur.execute("COMMIT; CREATE EXTENSION IF NOT EXISTS vector;")
    conn.commit()
    
pool.putconn(conn)

def create_users_table():
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    re_password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    documents_table TEXT,
                    chat_table TEXT
                )
            """)
            conn.commit()
            print("✅ Users table created successfully!")
    except psycopg2.Error as e:
        print(f"❌ Error creating users table: {e}")
    finally:
        pool.putconn(conn)
create_users_table()


def create_uploads(user_id_safe):
    """Creates a new structured documents table and chat history table for a new user."""
    documents_table = f"structured_documents_{user_id_safe}"
    chat_table = f"chat_history_{user_id_safe}"
    
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            # Create table for structured documents
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {documents_table} (
                    id SERIAL PRIMARY KEY,
                    heading TEXT,
                    content TEXT,
                    embedding VECTOR(384)
                );
            """)
            conn.commit()

            # Create table for chat history
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {chat_table} (
                    id SERIAL PRIMARY KEY,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
    except Exception as e:
        print(f"❌ Error creating tables for user {user_id_safe}: {e}")
    finally:
        pool.putconn(conn)
