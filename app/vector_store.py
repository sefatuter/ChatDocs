import numpy as np
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from database_conn import conn

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

def store_documents(documents):
    """Splits documents into chunks, generates embeddings, and stores them in PostgreSQL.
    Prevents duplicate uploads by checking if the content already exists.
    """
    all_splits = text_splitter.split_documents(documents)
    
    with conn.cursor() as cur:
        for doc in all_splits:
            heading = doc.metadata.get("source", "Unknown")
            content = sanitize_content(doc.page_content)
            
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