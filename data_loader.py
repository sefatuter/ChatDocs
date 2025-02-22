from langchain_community.document_loaders import PyMuPDFLoader, WebBaseLoader

def load_documents():
    """Loads PDF and Web documents"""
    # web_loader = WebBaseLoader("https://pgbackrest.org/user-guide.html")
    pdf_loader = PyMuPDFLoader("postgresql-17-A4.pdf")  

    # web_data = web_loader.load()
    pdf_data = pdf_loader.load()
    
    return pdf_data  # Merge both sources
