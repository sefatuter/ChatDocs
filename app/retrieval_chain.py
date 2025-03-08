from langchain_ollama import OllamaLLM
from vector_store import search_documents
from config import OLLAMA_API_BASE, OLLAMA_BASE_URL , OLLAMA_MODEL # Use OLLAMA_BASE_URL if running locally, Use OLLAMA_API_BASE for docker build
import re

# Initialize Ollama LLM
ollama = OllamaLLM(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)

def get_response(question, chat_history=[]):
    """Retrieve relevant documents and generate a response"""
    retrieved_docs = search_documents(question)
    
    # Extract content from retrieved documents
    context = "\n\n".join([doc[1] for doc in retrieved_docs]) 
    context = re.sub(r'\n{2,}', '\n', context)

    formatted_prompt = f"""
        You are a highly efficient assistant with expertise in analyzing diverse documents. Use the provided context to answer the user's question as accurately and concisely as possible.

        **Context**:  
        {context}

        **User Question**:  
        {question}

        **Instructions**:  
        1. Provide a concise, step-by-step explanation based on the context.  
        2. Include relevant examples, code, or commands (e.g., SQL if applicable) with proper syntax.  
        3. Highlight efficiency tips, best practices, or key insights relevant to the context.  

        **Response Format**:  
        - Use Markdown for clarity and structure.  
        - If the context is insufficient or irrelevant, respond with: *'I don’t have enough information to answer this based on the provided context.'*

        Keep the response focused, actionable, and optimized for the user’s needs.
        """

    response = ollama.invoke(formatted_prompt, options={"num_ctx": 8192, "temperature": 0.5})
    return response

