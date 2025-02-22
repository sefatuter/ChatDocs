import os
from langchain_community.document_loaders import PyMuPDFLoader, WebBaseLoader

def load_pdf(file_path):
    """Load documents from a PDF file."""
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    return documents

def load_website(url):
    """Load documents from a website URL."""
    loader = WebBaseLoader(url)
    documents = loader.load()
    return documents

def load_documents(file=None, website_url=None, upload_folder=None):
    """Load documents from either a PDF file or a website URL."""
    documents = []
    
    if file and file.filename != '':
        if upload_folder is None:
            raise ValueError("upload_folder must be provided when loading a file")
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        documents = load_pdf(file_path)
        os.remove(file_path)  # Clean up the file after loading
    elif website_url and website_url.strip() != '':
        documents = load_website(website_url)
    
    return documents