from flask_app.database.database import db


class users(db.Model):
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


# class User(flask.database.database.db.Model):
#     id = flask.database.database.db.Column("id", flask.database.database.db.Integer, primary_key=True)
#     name = flask.database.database.db.Column("name", flask.database.database.db.String(100))
#     email = flask.database.database.db.Column("email", flask.database.database.db.String(100))

#     def __init__(self, name, email):
#         self.name = name
#         self.email = email