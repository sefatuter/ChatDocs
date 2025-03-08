import os
from flask import Flask
from blueprints.chat import chat_bp
from blueprints.upload import upload_bp
from blueprints.account import account_bp
from blueprints.database import database_bp

app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv("FLASK_SECRET", "secret_key")

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.register_blueprint(chat_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(account_bp)
app.register_blueprint(database_bp)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)