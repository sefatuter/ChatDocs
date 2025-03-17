from flask import Blueprint, request, session, jsonify, render_template
import markdown
from retrieval_chain import get_response
from database_conn import pool
import psycopg2
from prompt_to_query import process_natural_language_query
from config import DEFAULT_DB_CONFIG    

query_bp = Blueprint('query_rt', __name__, template_folder='templates')

@query_bp.route('/databases', methods=['GET', 'POST'])
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

@query_bp.route("/execute_prompt", methods=["POST"])
def execute_prompt():
    selected_db = session.get("selected_db")
    
    if not selected_db:
        return jsonify({"error": "No database selected"}), 400
    
    prompt = request.form.get("prompt")
    print("Executing Prompt:", prompt)
    print("Executing on: ", selected_db)
    if not prompt:
        return jsonify({"error": "No user prompt provided"}), 400
    
    conn = None
    try:
        nl_response, executed_query = process_natural_language_query(prompt, selected_db)
        
        conn = psycopg2.connect(**DEFAULT_DB_CONFIG, dbname=selected_db)
        cur = conn.cursor()
        
        cur.execute(executed_query)
        
        if executed_query.strip().lower().startswith("select"):
            # For SELECT queries, get the column names and results
            columns = [desc[0] for desc in cur.description]
            
            result = cur.fetchall()
            
            cur.close()
            conn.close()
            
            return render_template(
                "database.html", 
                selected_db=selected_db, 
                tables=get_tables(selected_db), 
                nl_response=nl_response,
                result=result,
                columns=columns,
                final_query=executed_query,
                databases=get_databases()
            )
        else:
            # For non-SELECT queries (INSERT, UPDATE, DELETE)
            affected_rows = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            
            message = f"Query executed successfully. {affected_rows} rows affected."
            return render_template(
                "database.html", 
                selected_db=selected_db, 
                tables=get_tables(selected_db), 
                nl_response=nl_response,
                message=message,
                final_query=executed_query,
                databases=get_databases()
            )
            
    except psycopg2.ProgrammingError as e:
        if conn:
            conn.rollback()
        error_message = f"SQL Error: {str(e)}"
        print(error_message)
        return render_template(
            "database.html", 
            selected_db=selected_db, 
            tables=get_tables(selected_db), 
            error=error_message,
            final_query=executed_query if 'executed_query' in locals() else None,
            databases=get_databases()
        )
        
    except Exception as e:
        if conn:
            conn.rollback()
        error_message = f"Processing Error: {str(e)}"
        print(error_message)
        return render_template(
            "database.html", 
            selected_db=selected_db, 
            tables=get_tables(selected_db), 
            error=error_message,
            final_query=executed_query if 'executed_query' in locals() else None, 
            databases=get_databases()
        )
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