from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import os
import markdown
from data_loader import load_documents
from vector_store import store_documents, create_table, conn
from retrieval_chain import get_response

app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv("FLASK_SECRET", "your-secret-key")

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    create_table()
    documents_exist = has_documents()
    
    if request.method == 'POST':
        file = request.files.get('pdf_file')
        website_url = request.form.get('website_url')
        
        documents = load_documents(file=file, website_url=website_url, upload_folder=app.config['UPLOAD_FOLDER'])
        
        if not documents:
            flash("Please upload a PDF or enter a website URL.")
            return render_template('upload.html', documents_exist=documents_exist)
        
        store_documents(documents)
        session['documents_loaded'] = True
        return redirect(url_for('chat'))
    
    return render_template('upload.html', documents_exist=documents_exist)

@app.route('/chat')
def chat():
    if not has_documents():
        flash("Upload documents first!")
        return redirect(url_for('upload'))
    
    with conn.cursor() as cur:
        cur.execute("SELECT role, message FROM chat_history ORDER BY id")
        chat_history = [{"role": row[0], "message": row[1]} for row in cur.fetchall()]
    
    return render_template('chat.html', chat_history=chat_history)

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    response = get_response(question)
    response_html = markdown.markdown(response, extensions=['fenced_code', 'codehilite'])
    
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO chat_history (role, message) VALUES (%s, %s)",
            ("user", question)
        )
        cur.execute(
            "INSERT INTO chat_history (role, message) VALUES (%s, %s)",
            ("assistant", response_html)
        )
        conn.commit()
    
    return jsonify({"response": response_html})

@app.route("/reset_database", methods=["POST"])
def reset_database():
    """Clears the database and chat history"""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM structured_documents;")
        cur.execute("DELETE FROM chat_history;")
        conn.commit()
    session.pop('documents_loaded', None)
    return jsonify({"status": "success", "message": "Database reset successfully"}), 200

# Functions
def has_documents():
    """Check if there are any documents in the database"""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM structured_documents")
        count = cur.fetchone()[0]
    return count > 0

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)