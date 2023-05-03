from flask import Flask, render_template, redirect
from flask import session, request
from flask_login import LoginManager, login_required
from flask_login import logout_user, login_user
from UserLogin import UserLogin
from User import User
from DataBase import DataBase
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import sqlite3

db = DataBase(sqlite3.connect("diary.db", check_same_thread=False))

app = Flask(__name__)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().from_db(user_id, db)

@app.route("/registration", methods=["GET", "POST"])
def authenticate():
    if request.method == "POST":
        mail = request.form["mail"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        last_name = request.form["last_name"]
        user_type = request.form["user_type"]
        user_info = (
            main,
            generate_password_hash(password),
            first_name,
            middle_name,
            last_name,
            user_type
        )
        db.create_user(user_info)
        return redirect("/self_profile")
    return render_template("register.html")

@app.route("/auth", methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        user_data = db.get_user_by_login(login)
        if check_password_hash(user_data[2], password):
            user = User(user_data)

        if user is not None:
            user_login = UserLogin().create(user)
            login_user(user_login)
            return redirect("/self_profile")
        else:
            return render_template("auth.html", error="Неверный логин или пароль")
    return render_template("auth.html")

@login_required
@app.route("/self_profile")
def self_profile():
    return render_template("self_profile.html", session=session)

if __name__ == "__main__":
    app.run()