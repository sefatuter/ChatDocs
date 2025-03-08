from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from database_conn import pool, create_uploads
import re
import uuid
import bcrypt

account_bp = Blueprint('account_rt', __name__, template_folder='templates')

@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')
        re_password = data.get('confirm_password')
        password_regex = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@#$%^&+=]).{8,}$')
        
        if not re.match(password_regex, password):
            flash('Password must be at least 8 characters long, include one uppercase letter, '
                  'one number, and one special character.')
            return render_template('register.html')
            
        if user_exists(username):
            flash(f"Username '{username}' is already taken.", 'error')
            return render_template('register.html')
            
        if create_user(username, password, re_password):
            flash("Registration successful! You can now log in.", 'success')
            return redirect(url_for('account_rt.login'))
        
        flash("Something went wrong, please try again.", 'error')

    return render_template('register.html')

@account_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = get_user_by_username(username)  # Fetch user from DB
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            flash("Invalid username or password", "error")
            return redirect(url_for('account_rt.login'))

        session['user_id'] = user['id']  # Store user ID in session
        session['username'] = user['username']
        
        flash("Login successful!", "success")
        return redirect(url_for('upload_rt.upload'))
    return render_template('login.html')

@account_bp.route('/logout')
def logout():
    session.clear() 
    flash("You have been logged out.", "success")
    return redirect(url_for('account_rt.login'))

# Functions

def get_user_by_username(username):
    """Fetch user details from the database by username."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, username, password_hash 
                FROM users 
                WHERE username = %s;
            """, (username,))
            user = cur.fetchone()
            if user:
                return {"id": user[0], "username": user[1], "password_hash": user[2]}
            return None  # User not found
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return None
    finally:
        release_db_connection(conn)
        
        
def get_db_connection():
    return pool.getconn()

def release_db_connection(conn):
    pool.putconn(conn)
    

def create_user(username, password, re_password):
    conn = get_db_connection()
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        hashed_re_password = bcrypt.hashpw(re_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (username, password_hash, re_password_hash) 
                VALUES (%s, %s, %s) RETURNING id;
            """, (username, hashed_password, hashed_re_password))

            user_id = cur.fetchone()[0]
            
            # Convert UUID
            user_id_safe = str(user_id).replace('-', '_')
            documents_table = f"structured_documents_{user_id_safe}"
            chat_table = f"chat_history_{user_id_safe}"
            
            # Store the table names in the users table
            cur.execute("""
                UPDATE users SET documents_table = %s, chat_table = %s WHERE id = %s;
            """, (documents_table, chat_table, user_id))
            
        conn.commit()
    
        create_uploads(user_id_safe)  # create tables for each user

        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False
    finally:
        release_db_connection(conn)


def user_exists(username):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            return cur.fetchone() is not None
    finally:
        release_db_connection(conn)