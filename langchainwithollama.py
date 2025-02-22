from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import PyMuPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import GPT4AllEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

# Initialize Ollama LLM
ollama = OllamaLLM(base_url="http://localhost:11434", model='llama3:instruct')

# Load and process the document
web_loader = WebBaseLoader("")
pdf_loader = PyMuPDFLoader("")  

web_data = web_loader.load()
pdf_data = pdf_loader.load()


# Split text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
all_splits = text_splitter.split_documents(web_data)

for a in all_splits:
    print(a.page_content)
    print("---------------------------")
print("===================================================================================")


# Create vector store
vectorstore = Chroma.from_documents(documents=all_splits, embedding=GPT4AllEmbeddings())

# ✅ Define a system instruction as part of the prompt template
system_instruction = """
You are an expert in PostgreSQL. Use the following retrieved context to answer the user's question.

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

# ✅ Create ConversationalRetrievalChain with system instruction
retrieval_chain = ConversationalRetrievalChain.from_llm(
    llm=ollama,
    retriever=vectorstore.as_retriever(),
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt": prompt_template},
)

# ✅ Ensure we provide a chat history (empty for first query)
chat_history = []  

# Define a query
question = "Database erişip bir kolonu nasıl gösteririm?"

# Get the response
response = retrieval_chain.invoke({
    "question": question,
    "chat_history": chat_history
})

print("\n📘 Answer:", response["answer"])
