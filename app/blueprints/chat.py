from flask import Blueprint, render_template, redirect, url_for, flash, session
from database_conn import pool

chat_bp = Blueprint('chat_rt', __name__, template_folder='templates')

@chat_bp.route('/chat')
def chat():
    if 'user_id' not in session:
        flash("You need to log in first.", "error")
        return redirect(url_for('account_rt.login')) 
    
    user_id = session['user_id']
    user_id_safe = str(user_id).replace('-', '_')
    chat_table = f"chat_history_{user_id_safe}" 
    
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT role, message FROM {chat_table} ORDER BY id")
            chat_history = [{"role": row[0], "message": row[1]} for row in cur.fetchall()]
    except Exception as e:
        print(f"❌ Error fetching chat history: {e}")
        chat_history = []
    finally:
        pool.putconn(conn)

    return render_template('chat.html', chat_history=chat_history)
