from flask import Flask, render_template, request, redirect
from search4web import search4letters
from markupsafe import escape
import sqlite3

app = Flask(__name__)\

dbconfig = {'host': '127.0.0.1',
                'user': 'root',
                'password': '55060013Pabl.',
                'database': 'search_log', }

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

if __name__ == '__main__':
    app.run()