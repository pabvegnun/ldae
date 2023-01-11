from flask import Flask, render_template, request, redirect, url_for, session
from search4web import search4letters
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime


app = Flask(__name__)\

dbconfig = {'host': '127.0.0.1',
                'user': 'root',
                'password': '55060013Pabl.',
                'database': 'search_log', }

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = '55060013Pabl.'

# Enter your database connection details below
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '55060013Pabl.'
app.config['MYSQL_DB'] = 'search_log'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/')
def hello() -> str:
    return redirect('/entry')


@app.route('/')
@app.route('/search_page')
def search_page() -> 'html':
    return render_template('search_page.html',
                           the_title='Welcome to search for letters on the web!')

@app.route('/')
@app.route('/search_page_anonymous')
def search_page_anonymous() -> 'html':
    import mysql.connector
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()
    _SQL = """insert into counter
        (user, counter)
        values (%s, %s)"""
    cursor.execute(_SQL, ('anonymous',
                          1,))
    conn.commit()
    date = datetime.now()
    date_return = str(date)
    return render_template('search_page_anonymous.html',
                           the_title='Welcome to search for letters on the web!', la_fecha=date_return)

@app.route('/results', methods=['POST','GET'])
def do_search() -> str:
    phrase = request.form['phrase']
    letters = request.form['letters']
    remote_addr = request.remote_addr
    res = search4letters(phrase, letters)

    import mysql.connector
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()

    _SQL = """insert into log
    (phrase, letters, ip, browser_string, results)
    values (%s, %s, %s, %s, %s)"""

    cursor.execute(_SQL, (phrase,
                      letters,
                      remote_addr,
                      session['username'],
                      str(res), ))
    conn.commit()
    return render_template('results.html', the_phrase=phrase, the_letters=letters, the_results=res, username=session['username'])

@app.route('/results_anonymous', methods=['POST','GET'])
def do_anonymous_search() -> str:
    phrase = request.form['phrase']
    letters = request.form['letters']
    remote_addr = request.remote_addr
    res = search4letters(phrase, letters)

    import mysql.connector
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()

    _SQL = """insert into log
    (phrase, letters, ip, browser_string, results)
    values (%s, %s, %s, %s, %s)"""

    cursor.execute(_SQL, (phrase,
                      letters,
                      remote_addr,
                      'anonymous',
                      'res', ))
    conn.commit()
    return render_template('results.html', the_phrase=phrase, the_letters=letters, the_results=res, username='anonymous')
@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    counter = Counter()
    return render_template('entry.html',
                           the_title='Welcome to search for letters on the web!')
class Counter():
    import mysql.connector
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS counter(user varchar(32) not null, counter INT not null)")




@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/login/new_user', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('new_user.html', msg=msg)

# http://localhost:5000/login/home - this will be the home page, only accessible for loggedin users
@app.route('/login/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        import mysql.connector
        conn = mysql.connector.connect(**dbconfig)
        cursor = conn.cursor()
        _SQL = """insert into counter
                (user, counter)
                values (%s, %s)"""
        cursor.execute(_SQL, (session['username'],
                              1,))
        conn.commit()
        date = datetime.now()
        date_return = str(date)
        return render_template('home.html', username=session['username'], la_fecha = date_return)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/login/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        visitas_totales = cursor.execute('SELECT count(*) from counter')
        visitas_totales = cursor.fetchone()
        visitas_usuario = cursor.execute(' SELECT * FROM counter WHERE USER = %s', (account['username'],))
        return render_template('profile.html', account=account, las_visitas_totales=visitas_totales, las_visitas_usuario=visitas_usuario)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()