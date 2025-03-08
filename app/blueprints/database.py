from flask import Blueprint, request, session, jsonify
import markdown
from retrieval_chain import get_response
from database_conn import pool

database_bp = Blueprint('database_rt', __name__, template_folder='templates')

@database_bp.route('/ask', methods=['POST'])
def ask():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    username = session['username']
    user_id_safe = str(user_id).replace('-', '_')  # Convert UUID for PostgreSQL
    chat_table = f"chat_history_{user_id_safe}" 
    
    question = request.json.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    response = get_response(question)
    response_html = markdown.markdown(response, extensions=['fenced_code', 'codehilite'])
    
    conn = pool.getconn()   
    try:
        with conn.cursor() as cur:
            # Insert question from user
            cur.execute(f"""
                INSERT INTO {chat_table} (role, message) VALUES (%s, %s)
            """, (username, question))
            
            # Insert assistant response
            cur.execute(f"""
                INSERT INTO {chat_table} (role, message) VALUES (%s, %s)
            """, ("assistant", response_html))
            
            conn.commit()
    except Exception as e:
        print(f"❌ Error storing chat history: {e}")
        return jsonify({"error": "Failed to store chat history"}), 500
    finally:
        pool.putconn(conn)

    return jsonify({"response": response_html})


@database_bp.route("/reset_database", methods=["POST"])
def reset_database():
    """Clears the database and chat history"""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    user_id_safe = str(user_id).replace('-', '_')  
    documents_table = f"structured_documents_{user_id_safe}"
    chat_table = f"chat_history_{user_id_safe}"
    
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {documents_table};")  # Delete user’s documents
            cur.execute(f"DELETE FROM {chat_table};")  # Delete user’s chat history
            conn.commit()
        
        session.pop('documents_loaded', None)  # Remove session data
        return jsonify({"status": "success", "message": "User's database reset successfully"}), 200

    except Exception as e:
        print(f"❌ Error resetting database for user {user_id}: {e}")
        return jsonify({"error": "Failed to reset user database"}), 500
    finally:
        pool.putconn(conn)