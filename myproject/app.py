from flask import Flask, render_template, request, redirect, url_for, session
from search4web import search4letters
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)\

dbconfig = {'host': '127.0.0.1',
                'user': 'root',
                'password': '55060013Pabl.',
                'database': 'search_log', }
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
                      'user_agent',
                      'res', ))
    conn.commit()
    return str(search4letters(phrase, letters))

@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html',
                           the_title='Welcome to search for letters on the web!')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    return render_template('login.html', msg='')

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
                return 'Logged in successfully!'
            else:
                # Account doesnt exist or username/password incorrect
                msg = 'Incorrect username/password!'
        # Show the login form with message (if any)
        return render_template('entry.html', msg=msg)

if __name__ == '__main__':
    app.run()