from flask_app.database.database import db


class User(db.Model):
    user_id = db.Column("user_id", db.Integer, primary_key=True)
    first_name = db.Column("first_name", db.String(255))
    last_name = db.Column("last_name", db.String(255))
    _username = db.Column("_username", db.String(255))
    _password = db.Column("_password", db.String(255))

    def __init__(self, first_name, last_name, _username, _password):
        self.first_name = first_name
        self.last_name = last_name
        self._username = _username
        self._password = _password

class Question(db.Model):
    question_id = db.Column("question_id", db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.Integer)
    title = db.Column("title", db.String(512))
    contents = db.Column("contents", db.String(4096))
    date_created = db.Column("date_created", db.DateTime)

    def __init__(self, user_id, title, contents, date_created):
        self.user_id = user_id
        self.title = title
        self.contents = contents
        self.date_created = date_created
