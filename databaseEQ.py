import sqlite3
from sqlite3 import Error


def sql_connection():
    try:
        con = sqlite3.connect('equity2.db')
        return con
    except Error:
        print('There was a database error while connecting to it')

def sql_table(con):
    cursorObj = con.cursor()
    try:
        cursorObj.execute("CREATE table if not exists equity(date, equity, difference, increase)")
    except Error:
        print('Table already exist')
        pass

    con.commit()

def sql_insert(con, entry):
    cursorObj = con.cursor()
    cursorObj.execute('INSERT OR IGNORE INTO equity(date, equity, difference, increase) VALUES(?,?,?,?)', entry)
    con.commit()

def sql_fetch(con):
    cursorObj = con.cursor()
    cursorObj.execute('SELECT * FROM equity')
    rows = cursorObj.fetchall()
    return rows