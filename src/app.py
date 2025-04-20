from flask import Flask, render_template, request, jsonify, redirect, url_for, session

from app.database.crud import register_user, login_user, get_user


"""
register(username, email, password)
login(username, password)
get_user(user_id) -> {'username': 'username'}
"""

app = Flask(__name__)
app.secret_key = 'paus_secret_key'

@app.route('/')
def index():
    # load user if logged in
    user = None
    if session.get('user_id'):
        user = get_user(session['user_id'])
    return render_template('landing_page.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('login_register.html',
                               active='login',
                               user=None)

    # POST → attempt login
    data = request.get_json() or request.form
    result = login_user(
        username=data.get('loginEmail'),
        password=data.get('loginPassword')
    )
    if result.get('user_id'):
        session['user_id'] = result['user_id']
        return jsonify(result), 200

    return jsonify({'error': result.get('error', 'Login failed')}), 401


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('login_register.html',
                               active='register',
                               user=None)

    # POST → attempt registration
    data = request.get_json() or request.form
    result = register_user(
        username=data.get('regName'),
        email=data.get('regEmail'),
        password=data.get('regPassword')
    )
    if result.get('user_id'):
        session['user_id'] = result['user_id']
        return jsonify(result), 200

    return jsonify({'error': result.get('error', 'Registration failed')}), 400

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/plataform')
def plataform():
    # protect this page if you want:
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('main_panel.html', user=get_user(session['user_id']))


if __name__ == '__main__':
    app.run(debug=True)