from db import db

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    middle_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    user_type = db.Column(db.String, nullable=False)


class Marks(db.Model):
    mark_id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.Integer, nullable=False)
    time = db.Column(db.String, nullable=False)