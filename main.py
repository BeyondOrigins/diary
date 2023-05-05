from flask import Flask, render_template, redirect
from flask import session, request, Response, url_for
from flask_login import LoginManager, login_required
from flask_login import logout_user, login_user
from UserLogin import UserLogin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from db import db_init, db
from models import Users, Marks, Img
from config import *

app = Flask(__name__)
login_manager = LoginManager(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///diary.db"
app.config["SECRET_KEY"] = "gityihkgoerp"

db_init(app)

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, Users)
# главная страница
@app.route("/")
def main_page():
    welcoming_text = ""
    try:
        user = Users.query.get(session['_user_id'])
        welcoming_text = f", {user.first_name + ' ' + user.middle_name}"
    except:
        pass
    return render_template("main_page.html", welcoming_text=welcoming_text)

# регистрация
@app.route("/registration", methods=["GET", "POST"])
def authenticate():
    try:
        logout_user()
    except:
        pass
    if request.method == "POST":
        mail = request.form["mail"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        last_name = request.form["last_name"]
        if len(Users.query.filter_by(mail=mail).all()) != 0:
            return render_template("register.html", error="Эта почта уже используется")
        try:
            user_type = request.form["user_type"]
        except:
            user_type = "pupil"
        user = Users(
            mail=mail,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            password=generate_password_hash(password),
            user_type=user_type,
            img_id=0
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/auth")
    return render_template("register.html")

# авторизация
@app.route("/auth", methods=["GET", "POST"])
def auth():
    try:
        logout_user()
    except:
        pass
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        user = Users.query.filter_by(mail=login).first()

        if user is not None:
            if not check_password_hash(user.password, password):
                return render_template("auth.html", error="Неверный пароль")
            user_login = UserLogin().create(user)
            login_user(user_login)
            return redirect("/self_profile")
        else:
            return render_template("auth.html", error="Не найдено пользователя с такой почтой")
    return render_template("auth.html")

# страница собственного профиля
@app.route("/self_profile", methods=["GET", "POST"])
@login_required
def self_profile():
    user = Users.query.get(session["_user_id"])
    path = f"/get_img/{user.img_id}"
    if user.img_id == 0:
        path = DEFAULT_AVATAR_PATH
    if request.method == "POST":
        if request.files["pic"]:
            pic = request.files["pic"]
            filename = secure_filename(pic.filename)
            mimetype = pic.mimetype
            if not filename or not mimetype:
                return render_template("self_profile.html", user=user, path=path, error="Фотография не соответствует требованиям")
            
            img = Img(img=pic.read(), name=filename, mimetype=mimetype, user_id=user.user_id)
            try:
                old_img = Img.query.filter_by(user_id=user.user_id)[0]
                db.session.delete(old_img)
                db.session.commit()
            except:
                pass
            db.session.add(img)
            db.session.commit()
            user.img_id = Img.query.all()[-1].img_id
            db.session.commit()
        
        mail = request.form["mail"]
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        last_name = request.form["last_name"]
        user.mail = mail
        user.first_name = first_name
        user.middle_name = middle_name
        user.last_name = last_name
        db.session.commit()
        return render_template("self_profile.html", user=user, path=f"/get_img/{user.img_id}")
    return render_template("self_profile.html", user=user, path=path)

@app.route("/get_img/<int:img_id>")
def get_img(img_id):
    try:
        img = Img.query.get(img_id)
    except:
        return "Фото не найдено"
    return Response(img.img, mimetype=img.mimetype)

@app.route("/my_marks")
@login_required
def my_marks():
    user = Users.query.get(session["_user_id"])
    marks_list = Marks.query.filter_by(user_id=user.user_id).all()
    marks = {}
    for mark in marks_list:
        try:
            marks[mark.subject].append(mark.mark)
        except:
            marks[mark.subject] = []
            marks[mark.subject].append(mark.mark)
    print(marks)

    return render_template("my_marks.html", marks=marks)

@app.errorhandler(401)
def unauthorized_error_handler(error):
    return redirect("/auth")

if __name__ == "__main__":
    app.run()