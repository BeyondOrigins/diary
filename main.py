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

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///diary.db"
app.config["SECRET_KEY"] = "gityihkgoerp"
app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "diary.el.notifications@gmail.com"
app.config["MAIL_DEFAULT_SENDER"] = "diary.el.notifications@gmail.com"
app.config["MAIL_PASSWORD"] = APP_PASSWORD

email = Mail(app)

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
            Здравствуйте, {user.last_name} {user.first_name} {user.middle_name}
            Вы успешно создали аккаунт на нашем сайте.
        """
        email.send(msg)
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

# посмотреть свой профиль
@app.route("/profile")
@login_required
def profile():
    user = get_user()
    path = f"/get_img/{user.img_id}"
    if user.img_id == 0 or Img.query.get(user.img_id) is None:
        path = DEFAULT_AVATAR_PATH
        if Img.query.get(user.img_id) is None:
            user.img_id = 0
            db.session.commit()
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
                return render_template("self_profile.html", user=user, path=path,
                    error="Файл небезопасен")
            
            img = Img(img=pic.read(), name=filename, mimetype=mimetype, user_id=user.user_id)
            try:
                old_img = Img.query.filter_by(user_id=user.user_id)[0]
                db.session.delete(old_img)
                db.session.commit()
            except:
                pass
            db.session.add(img)
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
        session["name"] = f"{user.first_name} {user.middle_name}"
        return redirect("/profile")
    return render_template("edit_profile.html", user=user, path=path)

@app.route("/get_img/<int:img_id>")
def get_img(img_id : int):
    try:
        img = Img.query.get(img_id)
    except:
        return None
    return Response(img.img, mimetype=img.mimetype)

# посмотреть оценки
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
            marks[mark.subject].append(mark)
        except:
            marks[mark.subject] = []
            marks[mark.subject].append(mark)

    title = "Мои оценки"
    return render_template("marks.html", marks=marks, title=title)

# посмотреть своих ученик
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

    return render_template("pupils.html", pupils=pupils,
    subject=get_user().subject)

@app.route("/schedule", methods=["GET"])
@login_required
def schedule():
    week = 0
    day = 0
    if "week" in dict(request.args).keys():
        week = int(request.args["week"])
        day = int(request.args["day"])
    elif "user-type-info" in dict(request.args).keys():
        user_type = get_user().user_type
        return [user_type]
    
    lessons_query = Lessons.query.filter_by(
            week_id=week,
            weekday=day,
            grade=get_user().grade
    ).all()
        
    lessons = [[] for i in range(len(lessons_query))]
    for lesson in lessons_query:
        lessons[lesson.order_number] = {
            "id" : lesson.lesson_id,
            "subject" : lesson.subject,
            "homework" : lesson.homework,
            "is_replaced" : lesson.is_replaced
        }
    if len(request.args) != 0:
        return lessons

    return render_template("schedule.html", lessons=lessons,
    weekday=WEEKDAYS[day], week=week, day=day)

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
            marks[mark.subject].append(mark)
        except:
            marks[mark.subject] = []
            marks[mark.subject].append(mark)

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

# добавить урок
@app.route("/add_lesson/<int:week>/<int:day>", methods=["GET", "POST"])
@login_required
@teacher_only
def add_lesson(week : int, day : int):
    lessons_query = Lessons.query.filter_by(
        week_id=week,
        weekday=day,
        grade=get_user().grade
    ).all()
    teachers_query = Users.query.filter_by(
            user_type="teacher"
        )
    teachers = []
    for teacher in teachers_query:
        teachers.append({
            "id" : teacher.user_id,
            "name" : f"{teacher.first_name} {teacher.middle_name}  {teacher.last_name}",
            "subject" : teacher.subject
    })

    if request.method == "POST":
        teacher_id = request.form["teacher"]
        subject = request.form["subject"]
        homework = request.form["homework"]
        is_replaced = not Users.query.get(teacher_id).subject == subject
        
        lesson = Lessons(
            week_id=week,
            weekday=day,
            subject=subject,
            grade=get_user().grade,
            homework=homework,
            teacher_id=teacher_id,
            order_number=len(lessons_query),
            is_replaced=is_replaced
        )
        db.session.add(lesson)
        db.session.commit()
        return redirect(f"/schedule/{week}/{day}")
    
    return render_template("add_lesson.html", teachers=teachers,
    week=week, day=day)

# удалить урок
@app.route("/delete_lesson/<int:lesson_id>", methods=["GET", "POST"])
@login_required
@teacher_only
def delete_lesson(lesson_id : int):
    lesson = Lessons.query.get(lesson_id)
    week = lesson.week_id
    day = lesson.weekday
    if request.method == "POST":
        db.session.delete(lesson)
        db.session.commit()
        lessons_query = Lessons.query.filter_by(
            week_id=lesson.week_id,
            weekday=lesson.weekday,
            grade=get_user().grade
        ).all()
        for lesson_ in lessons_query:
            lesson_.order_number = lessons_query.index(lesson_)
            db.session.commit()
        return redirect(f"/schedule/{week}/{day}")
    day = WEEKDAYS[day]
    return render_template("delete_lesson.html", lesson=lesson, 
                           day=day)

# изменить данные урока
@app.route("/edit_lesson/<int:lesson_id>", methods=["GET", "POST"])
@login_required
@teacher_only
def edit_lesson(lesson_id : int):
    lesson = Lessons.query.get(lesson_id)
    teachers_query = Users.query.filter_by(
        user_type="teacher"
    )
    teachers = []
    for teacher in teachers_query:
        teachers.append({
            "id" : teacher.user_id,
            "name" : f"{teacher.first_name} {teacher.middle_name}  {teacher.last_name}",
            "subject" : teacher.subject
    })
        
    if request.method == "POST":
        subject = request.form["subject"]
        teacher_id = request.form["teacher"]
        homework = request.form["homework"]
        is_replaced = not Users.query.get(teacher_id).subject == subject
        
        lesson.subject = subject
        lesson.teacher_id = teacher_id
        lesson.homework = homework
        lesson.is_replaced = is_replaced
        db.session.commit()
        return redirect(f"/schedule/{lesson.week_id}/{lesson.weekday}")

    return render_template("edit_lesson.html", teachers=teachers,
        teacher_id=lesson.teacher_id, lesson=lesson)

# поставить оценки
@app.route("/pupils/marks/<int:pupil_id>")
@login_required
@teacher_only
def subject_marks(pupil_id : int):
    pupil = Users.query.get(pupil_id)
    user = get_user()
    marks = Marks.query.filter_by(
        user_id=pupil.user_id,
        subject=user.subject
    ).all()
    name = f"{pupil.last_name} {pupil.first_name} {pupil.middle_name}"
    return render_template("subject_marks.html", 
        marks=marks, subject=user.subject, name=name,
        pupil_id=pupil.user_id)

# посмотреть оценку
@app.route("/mark/<int:mark_id>")
@login_required
def mark(mark_id : int):
    mark = Marks.query.get(mark_id)
    user = get_user()
    pupil = Users.query.get(mark.user_id)
    if user.user_type == "pupil":
        if mark.user_id != user.user_id:
            abort(404)
        return render_template("mark.html", mark=mark, is_managable=False)
    else:
        if pupil.grade != user.grade and mark.subject != user.subject:
            abort(404)
        if mark.subject == user.subject:
            is_managable=True
        else:
            is_managable=False
        author = Users.query.get(mark.author_id)
        author_name = f"{author.last_name} {author.first_name} {author.middle_name}"
        return render_template("mark.html", mark=mark, is_managable=is_managable,
        author_name=author_name)

# удалить оценку
@app.route("/delete_mark/<int:mark_id>", methods=["GET", "POST"])
@login_required
@teacher_only
def delete_mark(mark_id : int):
    mark = Marks.query.get(mark_id)
    pupil = Users.query.get(mark.user_id)
    if pupil.grade != get_user().grade or mark.subject != get_user().subject:
        abort(404)
    if request.method == "POST":
        db.session.delete(mark)
        db.session.commit()
        return redirect(f"/pupils/marks/{pupil.user_id}")
    return render_template("delete_mark.html", mark=mark)

# добавить оценку
@app.route("/add_mark/<int:pupil_id>", methods=["GET", "POST"])
@login_required
@teacher_only
def add_mark(pupil_id):
    pupil = Users.query.get(pupil_id)
    if request.method == "POST":
        mark = request.form["mark"]
        subject = get_user().subject
        topic = request.form["topic"]
        task_type = request.form["task_type"]
        author_id = get_user().user_id
        mark = Marks(
            user_id=pupil_id,
            subject=subject,
            mark=mark,
            topic=topic,
            task_type=task_type,
            author_id=author_id
        )
        db.session.add(mark)
        db.session.commit()
        return redirect(f"/pupils/marks/{pupil.user_id}")
    return render_template("add_mark.html", pupil=pupil)

@app.route("/edit_mark/<int:mark_id>", methods=["GET", "POST"])
@login_required
@teacher_only
def edit_mark(mark_id : int):
    mark = Marks.query.get(mark_id)
    pupil = Users.query.get(mark.user_id)
    if request.method == "POST":
        mark.mark = request.form["mark"]
        mark.subject = get_user().subject
        mark.topic = request.form["topic"]
        mark.task_type = request.form["task_type"]
        db.session.commit()
        return redirect(f"/pupils/marks/{pupil.user_id}")
    return render_template("edit_mark.html", mark=mark)

# удалить фото профиля
@app.route("/delete_img/<img_id>", methods=["GET", "POST"])
@login_required
def delete_img(img_id : int):
    if request.method == "POST":
        user = get_user()
        img = Img.query.get(img_id)
        db.session.delete(img)
        user.img_id = 0
        db.session.commit()
        return redirect("/profile")
    return render_template("delete_img.html")

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
    app.run(debug=True, port=3000)
