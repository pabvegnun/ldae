import sqlite3

dbconfig = { 'host': '127.0.0.1',
             'user': 'root',
             'password': '55060013Pabl.',
             'database': 'search_log', }

import mysql.connector
conn = mysql.connector.connect(**dbconfig)
cursor = conn.cursor()
_SQL = """show tables"""
cursor.execute(_SQL)
res = cursor.fetchall()
print(res)

_SQL = """insert into log
        (phrase, letters, ip, browser_string, results)
        values (%s, %s, %s, %s, %s)"""
cursor.execute(_SQL, ('prueba',
                      'uea',
                      'prueba 127.0.0.1',
                      'otra_prueba',
                      'campo prueba', ))

_SQL = """select * from log"""
cursor.execute(_SQL)
res = cursor.fetchall()
print(res)

conn.commit()