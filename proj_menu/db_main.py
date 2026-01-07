import os.path
import sqlite3
import sys
from path_helper import get_writable_path

class DatabaseException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return f"Ошибка базы данных: {self.msg}." 
    
def connect_db(file_name, auto_create_db=False):
    try:
        path = get_writable_path(file_name)
        
        if not os.path.exists(path) and getattr(sys, 'frozen', False):
            print(f"DEBUG: Создаем новую БД в exe режиме: {path}")
            auto_create_db = True
        
        conn = sqlite3.connect(path)
        
        if auto_create_db:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    login TEXT NOT NULL COLLATE BINARY,
                    password TEXT NOT NULL COLLATE BINARY,
                    description TEXT,
                    birth_date TEXT,
                    type NUMERIC NOT NULL DEFAULT 1,
                    CONSTRAINT LOGIN PRIMARY KEY(login) ON CONFLICT ROLLBACK
                )
            ''')
            conn.commit()
            print(f"DEBUG: Создана/проверена таблица в {path}")
        
        return conn
    except Exception as e:
        print(f"ERROR в connect_db: {e}")
        raise DatabaseException(str(e))

def request_select_db(conn, query, args):
    try:
        cursor = conn.cursor()
        cursor.execute(query, args)
        return cursor.fetchall()
    except Exception as e:
        print(f"ERROR в request_select_db: {e}")
        raise DatabaseException(str(e))

def disconnect_db(conn):
    try:
        conn.close()
    except:
        pass

def request_update_db(conn, query, args):
    try:
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
    except Exception as e:
        print(f"ERROR в request_update_db: {e}")
        raise DatabaseException(str(e))
