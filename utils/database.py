import sqlite3

def connect_database(database_path):
    conn = sqlite3.connect(database_path)
    return conn
