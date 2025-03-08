from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from data_loader import load_documents
from vector_store import store_documents
from database_conn import pool
from flask import current_app

upload_bp = Blueprint('upload_rt', __name__, template_folder='templates')

@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        flash("You need to log in first.", "error")
        return redirect(url_for('account_rt.login'))
    
    user_id = session['user_id']
    documents_exist = has_documents(user_id=user_id)
    
    if request.method == 'POST':
        file = request.files.get('pdf_file')
        website_url = request.form.get('website_url')
        
        documents = load_documents(file=file, website_url=website_url, upload_folder=current_app.config['UPLOAD_FOLDER'])
        
        if not documents:
            flash("Please upload a PDF or enter a website URL.")
            return render_template('upload.html', documents_exist=documents_exist)
        
        store_documents(user_id=user_id, documents=documents)
        session['documents_loaded'] = True
        return redirect(url_for('chat_rt.chat'))
    
    return render_template('upload.html', documents_exist=documents_exist)


def has_documents(user_id):
    """Check if the user already has uploaded documents in their table."""
    user_id_safe = str(user_id).replace('-', '_')  
    documents_table = f"structured_documents_{user_id_safe}"

    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {documents_table};")
            count = cur.fetchone()[0]
            return count > 0
    except Exception as e:
        print(f"❌ Error checking documents for user {user_id}: {e}")
        return False
    finally:
        pool.putconn(conn)