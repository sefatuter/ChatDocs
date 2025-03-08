from flask import Blueprint, render_template, redirect, url_for, flash
from database_conn import conn

chat_bp = Blueprint('chat_rt', __name__, template_folder='templates')

@chat_bp.route('/chat')
def chat():
    if not has_documents():
        flash("Upload documents first!")
        return redirect(url_for('upload'))
    
    with conn.cursor() as cur:
        cur.execute("SELECT role, message FROM chat_history ORDER BY id")
        chat_history = [{"role": row[0], "message": row[1]} for row in cur.fetchall()]
    
    return render_template('chat.html', chat_history=chat_history)

def has_documents():
    """Check if there are any documents in the database"""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM structured_documents")
        count = cur.fetchone()[0]
    return count > 0