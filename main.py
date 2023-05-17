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
from models import Users, Marks, Img, Lessons
from config import *
from flask_mail import Message, Mail
from functools import wraps
from statistics import mean
from flask import abort

app = Flask(__name__)
login_manager = LoginManager(app)
email = Mail(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///diary.db"
app.config["SECRET_KEY"] = "gityihkgoerp"
app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "dima.a.ivlev@gmail.com"
app.config["MAIL_DEFAULT_SENDER"] = "dima.a.ivlev@gmail.com"
app.config["MAIL_PASSWORD"] = APP_PASSWORD

def teacher_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user()
        if user.user_type != "teacher":
            return render_template(
                "error.html",
                error="Эта страница доступна только учителям!"
            )
        return f(*args, **kwargs)
    return decorated_function

def pupil_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user()
        if user.user_type != "pupil":
            return render_template(
                "error.html",
                error="Эта страница доступна только ученикам!"
            )
        return f(*args, **kwargs)
    return decorated_function

def get_user():
    return Users.query.get(session["_user_id"])

db_init(app)

@login_manager.user_loader
def load_user(user_id : int):
    return UserLogin().fromDB(user_id, Users)

# главная страница
@app.route("/")
def main_page():
    welcoming_text = ""
    try:
        user = get_user()
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
        grade = request.form["grade_number"] + request.form["grade_letter"]
        if len(Users.query.filter_by(mail=mail).all()) != 0:
            return render_template("register.html", error="Эта почта уже используется")
        try:
            user_type = request.form["user_type"]
            subject = request.form["subject"]
            teachers = Users.query.filter_by(
                user_type="teacher",
                grade=grade
            ).all()
            if len(teachers) != 0:
                return render_template(
                    "register.html",
                    error="У этого класса уже есть классный руководитель")
        except:
            user_type = "pupil"
            subject = ""
        user = Users(
            mail=mail,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            password=generate_password_hash(password),
            user_type=user_type,
            img_id=0,
            grade=grade,
            subject=subject
        )
        db.session.add(user)
        db.session.commit()
        msg = Message("Регистрация прошла успешно",
                      sender="dima.a.ivlev@gmail.com",
                      recipients=[
                      user.mail
                      ])
        msg.body = f"""
            Здравствуйте, {user.first_name} {user.middle_name}
            Вы успешно создали аккаунт на нашем сайте.
        """
        # email.send(msg)
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
            session["name"] = f"{user.first_name} {user.middle_name}"
            session["grade"] = user.grade
            session["subject"] = user.subject
            session["user_type"] = user.user_type
            return redirect("/profile")
        else:
            return render_template("auth.html", error="Не найдено пользователя с такой почтой")
    return render_template("auth.html")

@app.route("/profile")
@login_required
def profile():
    user = get_user()
    path = f"/get_img/{user.img_id}"
    if user.img_id == 0:
        path = DEFAULT_AVATAR_PATH
    return render_template("profile.html", user=user, path=path)

# изменить параметры своего профиля
@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    user = get_user()
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
            user.img_id = Img.query.filter_by(user_id=user.user_id).all()[0].img_id
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
        return redirect("/profile")
    return render_template("edit_profile.html", user=user, path=path)

@app.route("/get_img/<int:img_id>")
def get_img(img_id : int):
    try:
        img = Img.query.get(img_id)
    except:
        return "Фото не найдено"
    return Response(img.img, mimetype=img.mimetype)

@app.route("/marks")
@login_required
def my_marks():
    user = get_user()
    if user.user_type == "teacher":
        return redirect("/pupils")
    marks_list = Marks.query.filter_by(user_id=user.user_id).all()
    marks = {}
    for mark in marks_list:
        try:
            marks[mark.subject].append(mark.mark)
        except:
            marks[mark.subject] = []
            marks[mark.subject].append(mark.mark)

    title = "Мои оценки"
    return render_template("marks.html", marks=marks, title=title)

@app.route("/pupils")
@login_required
@teacher_only
def pupils():
    user = get_user()
    pupils_list = Users.query.filter_by(
            user_type="pupil"
        )
    pupils = {}
    for pupil in pupils_list:
        marks_list = Marks.query.filter_by(
            user_id=pupil.user_id,
            subject=user.subject).all()
        marks = [mark.mark for mark in marks_list]
        average = round(mean(marks), 2) if len(marks) != 0 else "Оценок нет"
        try:
            pupils[pupil.grade][pupil] = average
        except:
            pupils[pupil.grade] = {}
            pupils[pupil.grade][pupil] = average

    return render_template("pupils.html", pupils=pupils)

@app.route("/schedule")
@login_required
def redirect_to_schedule():
    return redirect("/schedule/0/0")

@app.route("/schedule/<int:week>/<int:day>")
@login_required
def schedule(week : int, day : int):
    lessons_query = Lessons.query.filter_by(week_id=week,
        weekday=day,
        grade=get_user().grade
    ).all()

    lessons = [[] for i in range(len(lessons_query))]

    for lesson in lessons_query:
        lessons[lesson.order_number] = {
            "id" : lesson.lesson_id,
            "subject" : lesson.subject,
            "homework" : lesson.homework
        }

    return render_template("schedule.html", lessons=lessons,
    weekday=WEEKDAYS[day], week=week, day=day)

# добавить урок
@app.route("/add_lesson/<int:week>/<int:day>", methods=["GET", "POST"])
@login_required
@teacher_only
def edit_schedule(week : int, day : int):
    if request.method == "POST":
        pass

    lessons_query = Lessons.query.filter_by(week_id=week,
        weekday=day,
        grade=get_user().grade
    ).all()

    lessons = [[] for i in range(len(lessons_query))]
    
    return render_template("add_lesson.html", lessons=lessons)

# удалить урок
@app.route("/delete_lesson/<int:lesson_id>", methods=["GET", "POST"])
@login_required
@teacher_only
def delete_lesson(lesson_id):
    lesson = Lessons.query.get(lesson_id)
    if request.method == "POST":
        lessons_query = Lessons.query.filter_by(
            week_id=lesson.week_id,
            weekday=lesson.weekday,
            grade=get_user().grade
        ).all()
        # ДОДЕЛАТЬ
    day = WEEKDAYS[lesson.weekday]
    return render_template("delete_lesson.html", lesson=lesson, 
                           day=day)

# посмотреть свой класс
@app.route("/my_class")
@login_required
@teacher_only
def my_class():
    user = get_user()
    pupils_list = Users.query.filter_by(
        grade=user.grade,
        user_type="pupil"
    )
    pupils = {}
    for pupil in pupils_list:
        marks_list = Marks.query.filter_by(user_id=pupil.user_id).all()
        marks = [mark.mark for mark in marks_list]
        average = round(mean(marks), 2) if len(marks) != 0 else "Оценок нет"
        pupils[pupil] = average

    return render_template("my_class.html", pupils=pupils)

# посмотреть оценки ученика
@app.route("/marks/<int:user_id>")
@login_required
@teacher_only
def marks(user_id : int):
    user = Users.query.get(user_id)
    teacher = get_user()
    if teacher.grade != user.grade:
        abort(404)
    marks_list = Marks.query.filter_by(user_id=user_id).all()
    marks = {}
    for mark in marks_list:
        try:
            marks[mark.subject].append(mark.mark)
        except:
            marks[mark.subject] = []
            marks[mark.subject].append(mark.mark)

    title = f"{user.last_name} {user.first_name} {user.middle_name}"
    return render_template("marks.html", marks=marks, title=title)

@app.route("/lesson/<int:lesson_id>")
@login_required
def show_lesson(lesson_id : int):
    lesson = Lessons.query.get(lesson_id)
    if lesson is None:
        abort(404)
    teacher = Users.query.get(lesson.teacher_id)
    teacher_name = f"{teacher.first_name} {teacher.middle_name}  {teacher.last_name}"
    return render_template("lesson.html", lesson=lesson, teacher_name=teacher_name)

@app.errorhandler(401)
def unauthorized_error_handler(error):
    return redirect("/auth")

@app.errorhandler(404)
def not_found_error_handler(error):
    return render_template("error.html", error="Страница не найдена :(")

@app.errorhandler(500)
def server_error_handler(error):
    return render_template("error.html", error="Кажется, у нас проблемы на сервере")

if __name__ == "__main__":
    app.run()