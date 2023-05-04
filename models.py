from db import db

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    middle_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    user_type = db.Column(db.String, nullable=False)
    img_id = db.Column(db.Integer)


class Marks(db.Model):
    mark_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    mark = db.Column(db.Integer, nullable=False)
    time = db.Column(db.String, nullable=False)


class Img(db.Model):
    img_id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    mimetype = db.Column(db.String, nullable=False)