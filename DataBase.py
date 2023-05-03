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
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE mail={user_id}")
            user_data = self.__cur.fetchone()
            return User(user_data)
        except:
            return None
    
    def get_user_by_mail(self, user_mail):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE mail={user_mail}")
            user_data = self.__cur.fetchone()
            return User(user_data)
        except:
            return None
    
    def create_user(self, user_data):
        print(1)
        self.__cur.execute("""INSERT INTO users(
        mail, password, first_name, middle_name,
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