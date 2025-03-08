from flask import Blueprint, request, session, jsonify
import markdown
from retrieval_chain import get_response
from vector_store import conn

database_bp = Blueprint('database_rt', __name__, template_folder='templates')

@database_bp.route('/ask', methods=['POST'])
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

@database_bp.route("/reset_database", methods=["POST"])
def reset_database():
    """Clears the database and chat history"""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM structured_documents;")
        cur.execute("DELETE FROM chat_history;")
        conn.commit()
    session.pop('documents_loaded', None)
    return jsonify({"status": "success", "message": "Database reset successfully"}), 200