from flask import Flask, render_template, redirect
from flask import session, request
from flask_login import LoginManager, login_required
from flask_login import logout_user, login_user
from UserLogin import UserLogin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from db import db_init, db
from models import Users, Marks

app = Flask(__name__)
login_manager = LoginManager(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///diary.db"


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().from_db(user_id, db)

@app.route("/")
def main_page():
    return render_template("main_page.html")

@app.route("/registration", methods=["GET", "POST"])
def authenticate():
    if request.method == "POST":
        mail = request.form["mail"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        last_name = request.form["last_name"]
        if db.get_user_by_mail(mail) is not None:
            return render_template("register.html", error="Эта почта уже используется")
        try:
            user_type = request.form["user_type"]
        except:
            user_type = "pupil"
        user = Users(
            mail,
            first_name,
            middle_name,
            last_name,
            generate_password_hash(password),
            user_type
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/auth")
    return render_template("register.html")

@app.route("/auth", methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        user = Users.query.filter_by(mail=login)

        if user is not None:
            if not check_password_hash(user.password, password):
                return render_template("auth.html", error="Неверный пароль")
            user_login = UserLogin().create(user)
            login_user(user_login)
            return redirect("/self_profile")
        else:
            return render_template("auth.html", error="Не найдено пользователя с такой почтой")
    return render_template("auth.html")

@app.route("/self_profile")
@login_required
def self_profile():
    return render_template("self_profile.html", session=session)

@app.errorhandler(401)
def unauthorized_error_handler(error):
    return redirect("/auth")

if __name__ == "__main__":
    app.run()