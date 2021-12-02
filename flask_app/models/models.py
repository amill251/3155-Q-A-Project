import sqlalchemy
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

class Answer(db.Model):
    answer_id = db.Column("answer_id", db.Integer, primary_key=True)
    question_id = db.Column("question_id", db.Integer)
    user_id = db.Column("user_id", db.Integer)
    contents = db.Column("contents", db.String(4096))
    date_created = db.Column("date_created", db.DateTime)

    def __init__(self, question_id, user_id, contents, date_created):
        self.question_id = question_id
        self.user_id = user_id
        self.contents = contents
        self.date_created = date_created

class AnswerVote(db.Model):
    
    answer_id = db.Column("answer_id", db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.Integer, primary_key=True)
    vote_id = db.Column("vote_id", db.Integer)

    def __init__(self, answer_id, user_id, vote_id):
        self.answer_id = answer_id
        self.user_id = user_id
        self.vote_id = vote_id

class Vote(db.Model):
    vote_id = db.Column("vote_id", db.Integer, primary_key=True)
    vote_name = db.Column("vote_name", db.String(64))

    def __init__(self, vote_id, vote_name):
        self.vote_id = vote_id
        self.vote_name = vote_name

class Report(db.Model):
    report_id = db.Column("report_id", db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.Integer)
    question_id = db.Column("question_id", db.Integer)
    answer_id = db.Column("answer_id", db.Integer)

    def __init__(self, user_id, question_id, answer_id):
        self.user_id = user_id
        self.question_id = question_id
        self.answer_id = answer_id 

class Reactions(db.Model):
    reaction_id = db.Column("reaction_id", db.Integer, primary_key= True)
    reaction_name = db.Column("reaction_name", db.Text)
    
    def __init__(self, reaction_name):
        self.reaction_name = reaction_name

class PostReactions(db.Model):
    post_reaction_id = db.Column("post_reaction_id", db.Integer, primary_key= True)
    reaction_id = db.Column("reaction_id", db.Integer)
    user_id = db.Column("user_id", db.Integer)
    question_id = db.Column("question_id", db.Integer)
    answer_id = db.Column("answer_id", db.Integer)

    def __init__(self, reaction_id, user_id, question_id, answer_id):
        self.user_id = user_id
        self.reaction_id = reaction_id
        self.question_id = question_id
        self.answer_id = answer_id