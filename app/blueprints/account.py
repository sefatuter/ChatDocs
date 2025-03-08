from flask import Blueprint, render_template

account_bp = Blueprint('account_rt', __name__, template_folder='templates')

@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@account_bp.route('/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')