from data_loader import load_documents
from vector_store import store_documents
from retrieval_chain import get_response

# ✅ Load and Store Documents
# documents = load_documents()
# store_documents(documents)
# print("✅ Documents stored successfully in PostgreSQL.")

# ✅ Query the system
question = "what should be the pgbackrest.conf file to backup from replicas?"
response = get_response(question)


print("\n📘 Answer:", response)
