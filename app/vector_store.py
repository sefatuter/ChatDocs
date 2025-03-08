import numpy as np
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from database_conn import pool

embedding_model = GPT4AllEmbeddings()

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


def sanitize_content(content):
    """Remove NUL (0x00) characters and other problematic bytes from content."""
    if isinstance(content, str):
        return content.replace('\x00', '')
    elif isinstance(content, bytes):
        return content.replace(b'\x00', b'').decode('utf-8', errors='replace')
    return content

def store_documents(user_id, documents):
    """Splits documents into chunks, generates embeddings, and stores them in PostgreSQL.
    Prevents duplicate uploads by checking if the content already exists.
    """
    user_id_safe = str(user_id).replace('-', '_')  
    documents_table = f"structured_documents_{user_id_safe}"
    
    all_splits = text_splitter.split_documents(documents)
    
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            all_splits = text_splitter.split_documents(documents)

            for doc in all_splits:
                heading = doc.metadata.get("source", "Unknown")
                content = sanitize_content(doc.page_content)

                cur.execute(f"SELECT 1 FROM {documents_table} WHERE content = %s", (content,))
                if cur.fetchone() is not None:
                    continue
                
                embedding = np.array(embedding_model.embed_query(content)).tolist()

                cur.execute(f"""
                    INSERT INTO {documents_table} (heading, content, embedding)
                    VALUES (%s, %s, %s)
                """, (heading, content, embedding))

            conn.commit()
            print(f"✅ Documents stored successfully for user {user_id}")
    except Exception as e:
        print(f"❌ Error storing documents for user {user_id}: {e}")
    finally:
        pool.putconn(conn)

def search_documents(user_id, query, top_n=5):
    """Search for relevant documents using pgvector"""
    user_id_safe = str(user_id).replace('-', '_')  
    documents_table = f"structured_documents_{user_id_safe}"  
    
    conn = pool.getconn()
    try:
        query_embedding = np.array(embedding_model.embed_query(query)).tolist()

        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT heading, content, (embedding <=> %s::vector) AS similarity
                FROM {documents_table}
                ORDER BY similarity ASC
                LIMIT %s;
            """, (query_embedding, top_n))

            results = cur.fetchall()
            return results
    except Exception as e:
        print(f"❌ Error searching documents for user {user_id}: {e}")
        return []
    finally:
        pool.putconn(conn)