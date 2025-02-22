# retrieval_chain.py
from langchain_ollama import OllamaLLM
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from vector_store import search_documents
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

# Initialize Ollama LLM
ollama = OllamaLLM(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)

# Define system prompt template
system_instruction = """
You are an expert in PostgreSQL. Use the retrieved context to answer the user's question.

Provide:
1. A clear and concise explanation.
2. Relevant SQL commands and syntax.
3. Best practices and security recommendations.

Ensure responses are formatted properly in Markdown.
"""

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template=system_instruction + "\n\nContext:\n{context}\n\nUser Question:\n{question}"
)

def get_response(question, chat_history=[]):
    """Retrieve relevant documents and generate a response"""
    retrieved_docs = search_documents(question)
    
    # Extract content from retrieved documents
    context = "\n\n".join([doc[1] for doc in retrieved_docs]) 
    print("===================================================================")
    print(context) 
    print("===================================================================")

    # ✅ Properly formatted input for Ollama
    formatted_prompt = f"""
    You are an expert in PostgreSQL. Use the retrieved context to answer the user's question.

    Context:
    {context}

    User Question:
    {question}

    Provide:
    1. A clear,step by step and concise explanation.
    2. Relevant SQL commands and syntax.
    3. Best practices and security recommendations.

    Ensure responses are formatted properly in Markdown.

    If the context is not relevant, respond with 'I don't know'.
    """

    response = ollama.invoke(formatted_prompt, options={"num_ctx": 8192, "temperature": 0.5})
    return response

