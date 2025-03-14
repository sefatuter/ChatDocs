from flask import Blueprint, request, session, jsonify, render_template
import markdown
from retrieval_chain import get_response
from database_conn import pool
import psycopg2

DEFAULT_DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "user": "postgres",
    "password": "psql1234",
}

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
        
@database_bp.route('/databases', methods=['GET', 'POST'])
def get_db():        
    """Render database selection page"""
    if request.method == 'POST':
        selected_db = request.form.get('database')
        session['selected_db'] = selected_db
        tables = get_tables(selected_db) if selected_db else []
    else:
        selected_db = session.get("selected_db", "")
        tables = get_tables(selected_db) if selected_db else []
    
    databases = get_databases()
    return render_template("database.html", databases=databases, selected_db=selected_db, tables=tables)

@database_bp.route("/execute_query", methods=["POST"])
def execute_query():
    """Execute SQL query on the selected database"""
    selected_db = session.get("selected_db")
    
    print("Selected Database:", selected_db)
    if not selected_db:
        return jsonify({"error": "No database selected"}), 400
    
    query = request.form.get("query")
    print("Executing Query:", query)
    if not query:
        return jsonify({"error": "No SQL query provided"}), 400

    try:
        conn = psycopg2.connect(**DEFAULT_DB_CONFIG, dbname=selected_db)
        cur = conn.cursor()
        cur.execute(query)

        if query.strip().lower().startswith("select"):
            results = cur.fetchall()
            print(results)
            columns = [desc[0] for desc in cur.description]
            cur.close()
            conn.close()
            return render_template("database.html", selected_db=selected_db, tables=get_tables(selected_db), result=results, columns=columns, databases=get_databases())

        else:
            # Commit for INSERT, UPDATE, DELETE
            conn.commit()
            cur.close()
            conn.close()
            return render_template("database.html", selected_db=selected_db, tables=get_tables(selected_db), message="Query executed successfully", databases=get_databases())

    except psycopg2.ProgrammingError as e:
        conn.rollback()  # Rollback in case of error
        return render_template("database.html", selected_db=selected_db, tables=get_tables(selected_db), error=f"SQL Error: {str(e)}", databases=get_databases())

    except psycopg2.Error as e:
        return render_template("database.html", selected_db=selected_db, tables=get_tables(selected_db), error=f"Database Error: {str(e)}", databases=get_databases())

    finally:
        if conn:
            conn.close()


def get_databases():
    """Fetch all databases in PostgreSQL"""
    try:
        conn = psycopg2.connect(**DEFAULT_DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return databases
    except Exception as e:
        print("Error fetching databases:", e)
        return []

def get_tables(dbname):
    """Fetch tables from the selected database"""
    try:
        conn = psycopg2.connect(**DEFAULT_DB_CONFIG, dbname=dbname)
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return tables
    except Exception as e:
        print("Error fetching tables:", e)
        return []