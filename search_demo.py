import ollama
import psycopg2

# PostgreSQL connection settings
DB_NAME = "pgllm"
DB_USER = "postgres"
DB_PASSWORD = "psql1234"
DB_HOST = "localhost"
DB_PORT = "5432"

# Function to generate embeddings using Ollama (bge-m3 model)
def get_embedding(text):
    response = ollama.embeddings(model="bge-m3:latest", prompt=text)
    print("Generated embedding length:", len(response["embedding"]))
    return response["embedding"]

# Query input
query = "write me a create partial index example"
print(f"\nQuery: {query}")
query_embedding = get_embedding(query)

# Connect to PostgreSQL
print("\nConnecting to PostgreSQL...")
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# Check vector extension
print("\nChecking vector extension...")
cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
conn.commit()

# Check table contents and sample data
print("\nChecking table contents...")
cur.execute("SELECT COUNT(*) FROM structured_documents;")
count = cur.fetchone()[0]
print(f"Number of records in table: {count}")

# Sample a few entries to understand the data
print("\nSampling some entries to understand the data:")
cur.execute("""
    SELECT heading, substring(content, 1, 100), length(content)
    FROM structured_documents 
    LIMIT 3;
""")
samples = cur.fetchall()
for sample in samples:
    print(f"\nHeading: {sample[0]}")
    print(f"Content preview: {sample[1]}...")
    print(f"Content length: {sample[2]}")

# Combined Vector Search Query with more flexible matching
print("\nExecuting search query...")
search_query = """
    WITH vector_matches AS (
        SELECT 
            heading, 
            content,
            embedding <-> vector(%s) AS similarity,
            ts_rank_cd(search_tsv, to_tsquery('english', %s)) AS text_rank
        FROM structured_documents
        ORDER BY similarity ASC
        LIMIT 20
    )
    SELECT 
        heading,
        content,
        similarity,
        text_rank
    FROM vector_matches
    ORDER BY similarity ASC
    LIMIT 5;
"""

# Convert search terms to tsquery format
search_terms = ' & '.join(query.split())
print(f"\nSearch terms: {search_terms}")

cur.execute(search_query, (str(query_embedding), search_terms))

# Fetch results
print("\nFetching results...")
results = cur.fetchall()
print(f"Number of results returned: {len(results)}")

# Display search results
if len(results) > 0:
    print("\nSearch Results:")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Heading: {result[0]}")
        print(f"Content: {result[1]}")
        print(f"Similarity Score: {result[2]}")
        print(f"Text Rank: {result[3]}")
else:
    print("\nNo results found. Please check if:")
    print("1. The vector dimensions match between the query and the database")
    print("2. The content is properly indexed")
    
    # Check vector dimensions
    cur.execute("""
        SELECT embedding[1:5]
        FROM structured_documents
        LIMIT 1;
    """)
    vec_sample = cur.fetchone()
    if vec_sample:
        print("\nSample vector from database (first 5 dimensions):", vec_sample[0])

cur.close()
conn.close()
print("\nConnection closed.")