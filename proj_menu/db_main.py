import os.path
import sqlite3

class DatabaseException(Exception):
    def __init__(self, msg):
        self.msg = msg
 
    def __str__(self):
        return f"Ошибка базы данных:{self.msg}." 
    
def connect_db(file_name,auto_create_db=False):
    if auto_create_db:
        conn = sqlite3.connect(file_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                login TEXT NOT NULL COLLATE BINARY,
                password TEXT NOT NULL COLLATE BINARY,
                type NUMERIC NOT NULL DEFAULT 1,
                CONSTRAINT LOGIN PRIMARY KEY(login) ON CONFLICT ROLLBACK
            )
        ''')
        conn.commit()
    else:
        path = file_name
        if os.path.isfile(path):
            conn = sqlite3.connect(file_name)
        else:
            raise DatabaseException(f"Файл ({file_name}) базы данных не найден")  
    return conn
    
def request_select_db(conn,query,args):
    if not isinstance(args, tuple):
        raise DatabaseException("Параметры запросы выборки имеют неверный тип")
    cursor = conn.cursor()
    try:
        cursor.execute(query,args)
    except sqlite3.Error as ex:
        raise DatabaseException(str(ex))
    rows = cursor.fetchall()
    data=[]
    for row in rows:
        data.append(row)
    return data

def disconnect_db(conn):
    conn.close()

def request_update_db(conn,query,args):
    if not isinstance(args, tuple):
        raise DatabaseException("Параметры запросы выборки имеют неверный тип")
    
    cursor = conn.cursor()
    try:
        cursor.execute(query,args)
    except sqlite3.Error as ex:
        raise DatabaseException(str(ex))
    conn.commit()


