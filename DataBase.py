from User import User
import datetime


class DataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()
        self.__cur.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        mail TEXT NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT NOT NULL,
        middle_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        user_type TEXT NOT NULL
        );""")
        self.__cur.execute("""CREATE TABLE IF NOT EXISTS marks(
        user_id INTEGER PRIMARY KEY,
        mark INTEGER NOT NULL,
        time TEXT NOT NULL
        );""")
        self.__db.commit()
    
    def get_user(self, user_id):
        self.__cur.execute(f"SELECT * FROM users WHERE user_id={user_id}")
        user_data = self.__cur.fetchone()
        if user_data is not None:
            return User(user_data)
        return None
    
    def get_user_by_login(self, user_login):
        self.__cur.execute(f"SELECT * FROM users WHERE user_login={user_login}")
        user_data = self.__cur.fetchone()
        if user_data is not None:
            return User(user_data)
        return None
    
    def create_user(self, user_data):
        self.__cur.execute("""INSERT INTO users(
        login, password, first_name, middle_name,
        last_name, user_type
        ) VALUES (?, ?, ?, ?, ?, ?);
        """, user_data)
        self.__db.commit()
    
    def delete_user(self, user_id):
        self.__cur.execute(f"DELETE FROM users WHERE user_id={user_id}")
        self.__cur.execute(f"DELETE FROM marks WHERE user_id={user_id}")
        self.__db.commit()
    
    def add_mark(self, user_id, mark):
        mark_info = (user_id, mark, datetime.datetime.now())
        self.__cur.execute(
            "INSERT INTO marks VALUES(?, ?, ?)", 
            mark_info
        )
        self.__db.commit()
    
    def execute(self, request: str, values=()):
        self.__cur.execute(request, values)
        self.__db.commit()