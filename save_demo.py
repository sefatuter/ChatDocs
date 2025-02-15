import ollama
import psycopg2
import json

DB_NAME = "pgllm"
DB_USER = "postgres"
DB_PASSWORD = "psql1234"
DB_HOST = "localhost"
DB_PORT = "5432"

# Load structured_data from JSON file
with open("structured_data.json", "r", encoding="utf-8") as f:
    structured_data = json.load(f)

print("Data Loaded.")


def get_embedding(text):
    response = ollama.embeddings(model="bge-m3:latest", prompt=text)
    return response["embedding"]

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()


# Insert data into structured_documents
for heading, content in structured_data:
    embedding_vector = get_embedding(content)  # Generate embedding

    cur.execute(
        """
        INSERT INTO structured_documents (heading, content, embedding)
        VALUES (%s, %s, %s)
        """,
        (heading, content, embedding_vector)
    )
    
# Commit and close
conn.commit()
cur.close()
conn.close()

print("Data inserted successfully into PostgreSQL with Ollama embeddings.")
