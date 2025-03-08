from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from data_loader import load_documents
from vector_store import store_documents
from database_conn import create_table, conn
from flask import current_app

upload_bp = Blueprint('upload_rt', __name__, template_folder='templates')

@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    create_table()
    documents_exist = has_documents()
    
    if request.method == 'POST':
        file = request.files.get('pdf_file')
        website_url = request.form.get('website_url')
        
        documents = load_documents(file=file, website_url=website_url, upload_folder=current_app.config['UPLOAD_FOLDER'])
        
        if not documents:
            flash("Please upload a PDF or enter a website URL.")
            return render_template('upload.html', documents_exist=documents_exist)
        
        store_documents(documents)
        session['documents_loaded'] = True
        return redirect(url_for('chat_rt.chat'))
    
    return render_template('upload.html', documents_exist=documents_exist)

def has_documents():
    """Check if there are any documents in the database"""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM structured_documents")
        count = cur.fetchone()[0]
    return count > 0