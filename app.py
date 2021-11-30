import os
import json
import re
import base64
from sqlite3.dbapi2 import Date
import datetime
import hmac
import hashlib
from flask import Flask, app, g, request, jsonify, redirect, url_for
from flask import render_template
import sqlite3
import jwt
from functools import wraps
from flask_app.database.database import db
from flask_app.models.models import Answer, User as User
from flask_app.models.models import Question as Question
from flask_app.models.models import AnswerVote as AnswerVote
from flask_app.models.models import Vote as Vote

DATABASE_PATH = './flask_app/database/database.db'


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__,
                static_url_path='',
                template_folder='./flask_app/templates',
                static_folder='./flask_app/static')

    config(app, test_config)
    init_db(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    page_routes(app)
    api_routes(app)

    return app


def page_routes(app):
    # Routes for Pages
    @app.route("/")
    def index():
        return render_template("login.html")

    @app.route("/signup")
    def signup():
        return render_template("createaccount.html")

    @app.route("/feed")
    @cookie_auth(app)
    def feed():
        return render_template("feed.html")

    @app.route("/ask-question")
    @cookie_auth(app)
    def createpost():
        return render_template("createpost.html")

    @app.route("/view-question")
    @cookie_auth(app)
    def viewpost():
        return render_template("viewquestion.html")
    
    @app.route("/edit-question")
    @cookie_auth(app)
    def editpost():
        return render_template("editquestion.html")

    @app.route("/profile")
    @cookie_auth(app)
    def profile():
        return render_template("profile.html")


def api_routes(app):
    # Routes for Pages
    @app.route("/api", methods=["GET", "POST"])
    @api_auth(app)
    def api():
        # this is a placeholder for testing

        return 'Okay'

    @app.route("/api/users/create-account", methods=["POST"])
    def create_account():
        f_name = request.json['first_name']
        l_name = request.json['last_name']
        _uname = request.json['_username']
        _pword = request.json['_password']

        message = bytes(_pword, 'utf-8')
        secret = bytes(app.config['SECRET_KEY'], 'utf-8')

        hash_pass = str(base64.b64encode(
            hmac.new(secret, message, digestmod=hashlib.sha256).digest()).decode())

        check_user = db.session.query(User).filter_by(_username=_uname).first()

        if check_user:
            return jsonify(succeed=False, message='Error: User ' + str(_uname) + ' already exists')

        new_record = User(f_name, l_name, _uname, hash_pass)
        db.session.add(new_record)
        db.session.commit()
        fetched_user = db.session.query(
            User).filter_by(_username=_uname).first()

        response = jsonify(succeed=True, message='User ' +
                           str(_uname) + ' created successfully')
        token_expires = 3600
        bearer_token = 'Bearer ' + jwt.encode({'user': _uname, 'user_id': fetched_user.user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(
            seconds=token_expires), 'expires_in': token_expires}, app.config['SECRET_KEY'], algorithm="HS256")

        response = jsonify(succeed=True, message='User ' +
                           str(_uname) + ' logged in successfully')
        base64_encoded_bearer = str(base64.b64encode(
            str.encode(bearer_token)).decode())
        response.set_cookie('bt', base64_encoded_bearer, httponly=True)
        response.set_cookie('exp', str(
            getBearerJwtPayload(bearer_token)['exp']))
        response.set_cookie('expires_in', str(
            getBearerJwtPayload(bearer_token)['expires_in']))
        response.set_cookie('user', str(
            getBearerJwtPayload(bearer_token)['user']))
        response.set_cookie('user_id', str(
            getBearerJwtPayload(bearer_token)['user_id']))

        return response

    @app.route("/api/users/logout", methods=["POST"])
    def logout_user():
        response = jsonify(succeed=True)
        response.set_cookie('bt', '', httponly=True)
        return response

    @app.route("/api/users/login", methods=["POST"])
    def login_user():

        _uname = request.json['_username']
        _pword = request.json['_password']

        fetched_user = db.session.query(
            User).filter_by(_username=_uname).first()

        if not fetched_user:
            return jsonify(succeed=False, message='User not found')

        hash_pass = bytes(str(_pword), 'utf-8')
        secret = bytes(app.config['SECRET_KEY'], 'utf-8')

        signature = str(base64.b64encode(
            hmac.new(secret, hash_pass, digestmod=hashlib.sha256).digest()).decode())

        if fetched_user._password == signature:
            token_expires = 3600
            bearer_token = 'Bearer ' + jwt.encode({'user': _uname, 'user_id': fetched_user.user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(
                seconds=token_expires), 'expires_in': token_expires}, app.config['SECRET_KEY'], algorithm="HS256")

            response = jsonify(succeed=True, message='User ' +
                               str(_uname) + ' logged in successfully')
            base64_encoded_bearer = str(base64.b64encode(
                str.encode(bearer_token)).decode())
            response.set_cookie('bt', base64_encoded_bearer, httponly=True)
            response.set_cookie('exp', str(
                getBearerJwtPayload(bearer_token)['exp']))
            response.set_cookie('expires_in', str(
                getBearerJwtPayload(bearer_token)['expires_in']))
            response.set_cookie('user', str(
                getBearerJwtPayload(bearer_token)['user']))
            response.set_cookie('user_id', str(
                getBearerJwtPayload(bearer_token)['user_id']))

            return response
        else:
            return jsonify(succeed=False, message='Incorrect Password')

    @app.route("/api/refresh-token", methods=["GET"])
    @cookie_auth(app)
    def refresh_token():

        cookie_token = request.cookies.get('bt')

        bearer_token = str(base64.b64decode(cookie_token).decode())
        token_expires = 3600
        
        fetched_user = db.session.query(
            User).filter_by(_username=getBearerJwtPayload(bearer_token)['user']).first()

        bearer_token = 'Bearer ' + jwt.encode({'user': getBearerJwtPayload(bearer_token)['user'], 'user_id': fetched_user.user_id, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(seconds=token_expires), 'expires_in': token_expires}, app.config['SECRET_KEY'], algorithm="HS256")

        base64_encoded_bearer = str(base64.b64encode(
            str.encode(bearer_token)).decode())

        response = jsonify(token=bearer_token)
        response.set_cookie('bt', base64_encoded_bearer, httponly=True)
        response.set_cookie('exp', str(
            getBearerJwtPayload(bearer_token)['exp']))
        response.set_cookie('expires_in', str(
            getBearerJwtPayload(bearer_token)['expires_in']))
        response.set_cookie('user', str(
            getBearerJwtPayload(bearer_token)['user']))
        response.set_cookie('user_id', str(
            getBearerJwtPayload(bearer_token)['user_id']))

        return response

    # Questions Questions Questions Questions Questions Questions Questions Questions

    @app.route("/api/questions", methods=["GET", "POST"])
    @api_auth(app)
    def questions():
        if request.method == "POST":
            print(request.json)
            u_id = request.json['user_id']
            bearer_token = request.headers['Authorization']
            user_id = getBearerJwtPayload(bearer_token)['user_id']
            if u_id is not user_id:
                return jsonify(succeed=False), 401
                
            title = request.json['title']
            contents = request.json['contents']
            d_created = datetime.datetime.now()

            new_record = Question(u_id, title, contents, d_created)
            db.session.add(new_record)
            db.session.commit()
            return jsonify(succeed=True)
        elif request.method == "GET":
            print('Method was GET')
            print(request.args)
            if request.args.__contains__('question'):
                print('Request has a json')
                try:
                    questionId = request.args['question']
                except:
                    return jsonify({'message': 'Question Body Invalid'}), 400

                question = db.session.query(Question).filter_by(
                    question_id=questionId).first()
                
                if not question:
                    return jsonify(succeed=False, message="Question not found"), 404
                
                user_name = db.session.query(User).filter_by(
                    user_id=question.user_id).first()._username

                question_dict = {
                    'question_id': question.question_id,
                    'user_id': question.user_id,
                    'title': question.title,
                    'contents': question.contents,
                    'date_created': question.date_created,
                    'username': user_name
                }

                questions_response = dict()
                questions_response['data'] = []

                questions_response['data'].append(question_dict)

                response = jsonify(questions_response)

                return response
            else:
                print('Doesnt have a json')
                fetched_questions = db.session.query(Question).all()

                questions_response = dict()
                questions_response['data'] = []

                for question in fetched_questions:
                    print(question)
                    user_name = db.session.query(User).filter_by(
                    user_id=question.user_id).first()._username
                    print(user_name)
                    question_dict = {
                        'question_id': question.question_id,
                        'user_id': question.user_id,
                        'title': question.title,
                        'contents': question.contents,
                        'date_created': question.date_created,
                        'username': user_name
                    }
                    questions_response['data'].append(question_dict)
                
                print('End of response')
                response = jsonify(questions_response)

                return response

    @app.route("/api/questions/delete", methods=["POST"])
    @api_auth(app)
    def deleteQuestion():  
        delete_question_id = request.json['delete']

        bearer_token = request.headers['Authorization']

        user_id = getBearerJwtPayload(bearer_token)['user_id']
        question = db.session.query(Question).filter_by(
            question_id=delete_question_id).first()
        if not question:
            return jsonify(succeed=False, message="Question not found"), 404
        print('Got the Question id')
        if question.user_id is user_id:
            Question.query.filter_by(question_id=delete_question_id).delete()
            Answer.query.filter_by(question_id=delete_question_id).delete()
            db.session.commit()
            return jsonify(succeed=True)
        else:
            return jsonify(succeed=False), 401

    @app.route("/api/questions/edit", methods=["POST"])
    @api_auth(app)
    def editQuestion():  
        if request.method == "POST":

            q_id = request.json['question_id']
            u_id = request.json['user_id']
            title = request.json['title']
            contents = request.json['contents']

            bearer_token = request.headers['Authorization']
            user_id = getBearerJwtPayload(bearer_token)['user_id']


            if u_id is not user_id:
                return jsonify(succeed=False), 401


            question = Question.query.filter_by(question_id=q_id).first()

            if not question:
                    return jsonify(succeed=False, message="Question not found"), 404


            if question.user_id is user_id:
                question.title = title
                question.contents = contents
                db.session.commit()
            else:
                return jsonify(succeed=False), 401

            return jsonify(succeed=True)


    @app.route("/api/answers", methods=["GET", "POST"])
    @api_auth(app)
    def answers():
        if request.method == "POST":
            print('Answers was called')
            bearer_token = request.headers['Authorization']
            user_id = getBearerJwtPayload(bearer_token)['user_id']
            q_id = request.json['question_id']
            contents = request.json['contents']
            d_created = datetime.datetime.now()

            new_record = Answer(q_id, user_id, contents, d_created)
            db.session.add(new_record)
            db.session.commit()
            return jsonify(succeed=True)
        elif request.method == "GET":
            bearer_token = request.headers['Authorization']
            user_id = getBearerJwtPayload(bearer_token)['user_id']
            questionId = request.args['question']
            answers = db.session.query(Answer).filter_by(
                    question_id=questionId).all()

            answers_response = dict()
            answers_response['data'] = []

            for answer in answers:
                user_name = db.session.query(User).filter_by(
                    user_id=answer.user_id).first()._username
                
                
                total_votes = {
                    'upvotes': AnswerVote.query.filter_by(answer_id=answer.answer_id, vote_id=1).count(),
                    'downvotes': AnswerVote.query.filter_by(answer_id=answer.answer_id, vote_id=2).count()
                }

                user_vote = 'novote'

                test_vote = Vote.query.join(AnswerVote, AnswerVote.vote_id==Vote.vote_id).filter_by(answer_id=answer.answer_id, user_id=user_id).first()

                if test_vote is not None:
                    user_vote = test_vote.vote_name


                answer_dict = {
                            'answer_id': answer.answer_id,
                            'question_id': answer.question_id,
                            'user_id': answer.user_id,
                            'contents': answer.contents,
                            'date_created': answer.date_created,
                            'username': user_name,
                            'votes': {
                                'total_votes': total_votes['upvotes'] - total_votes['downvotes'],
                                'uservotes': user_vote
                            }
                        }
                
                answers_response['data'].append(answer_dict)
                
            response = jsonify(answers_response)

            return response

        return 0

    @app.route("/api/votes", methods=["GET", "POST"])
    @api_auth(app)
    def votes():
        print('Got to vote')
        if request.method == "POST":
            print('Got to POST vote')
            bearer_token = request.headers['Authorization']
            print('Got 5555')
            u_Id = getBearerJwtPayload(bearer_token)['user_id']
            print('Got 7777')
            a_Id = request.json['answer_id']
            print('Got past answerId')
            vote_name = request.json['vote_name']
            print('Got 88888')
            try:
                current_vote = db.session.query(AnswerVote).filter_by(user_id=u_Id, answer_id=a_Id).first()
            except Exception as e:
                print(e)
            current_vote = db.session.query(AnswerVote).filter_by(
                    user_id=u_Id, answer_id=a_Id).first()

            print(current_vote)
            current_vote_id = db.session.query(Vote).filter_by(
                    vote_name=vote_name).one().vote_id
            print('got throught votes')
            if current_vote is None:
                print('In current vote 1')
                print(a_Id)
                print(u_Id)
                print(AnswerVote.query.filter_by(answer_id=1, user_id=2).first())
                print(AnswerVote.query.filter_by(answer_id=1, user_id=2, vote_id=2).first())
                new_record = AnswerVote(a_Id, u_Id, current_vote_id)
                # new_record = AnswerVote(2, 1, 2)
                print(new_record)
                print('In current vote 2')
                db.session.add(new_record)
                print(new_record)
                print('In current vote 2.5')
                try:
                    db.session.commit()
                except Exception as e:
                    print(e)

                print('In current vote 3')
                return jsonify(success=True)
            elif current_vote.vote_id is current_vote_id:
                print('Current vote is Vote ID')
                AnswerVote.query.filter_by(user_id=u_Id, answer_id=a_Id).delete()
                db.session.commit()
                return jsonify(success=True)
            elif current_vote.vote_id is not current_vote_id:
                print('Current is not Vote name')
                current_vote.vote_id = current_vote_id
                db.session.commit()
                return jsonify(success=True)
            return jsonify(success=False, message='Vote type not found')
        elif request.method == "GET":
            bearer_token = request.headers['Authorization']
            u_Id = getBearerJwtPayload(bearer_token)['user_id']
            q_Id = request.args['question']
            question_votes = db.session.query(AnswerVote).join(Answer, Answer.answer_id==AnswerVote.answer_id).filter_by(question_id=q_Id)
            votes_response = dict()
            votes_response['data'] = []
            for vote in question_votes:
                print(vote.answer_id)
                print(vote.user_id)
                print(vote)
                vote_dict = {
                            'answer_id': vote.answer_id,
                            'user_id': vote.user_id,
                            'vote_id': vote.vote_id
                        }
                
                votes_response['data'].append(vote_dict)

            return jsonify(votes_response)

        return 0

def api_auth(app):
    def api_auth_decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):

            bearer_token = request.headers.get('Authorization')

            print(bearer_token)

            if not bearer_token:
                return jsonify({'message': 'Token is missing'}), 401
            print('Past 1')
            if bool(re.search('^Bearer\s+(.*)', bearer_token)):
                token = bearer_token.replace('Bearer ', '')
            else:
                return jsonify({'message': 'Bearer Token is invalid'}), 401
            print('Past 2')

            try:
                jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
                print('Past 3')
                return func(*args, **kwargs)
            except:
                return jsonify({'message': 'Bearer Token is invalid'}), 401
        return decorated
    return api_auth_decorator


def cookie_auth(app):
    def view_auth_decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):

            cookie_token = request.cookies.get('bt')

            if not cookie_token:
                return redirect(url_for('index'))

            bearer_token = str(base64.b64decode(cookie_token).decode())

            if not bearer_token:
                return redirect(url_for('index'))

            if bool(re.search('^Bearer\s+(.*)', bearer_token)):
                token = bearer_token.replace('Bearer ', '')
            else:
                return redirect(url_for('index'))

            try:
                jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
                return func(*args, **kwargs)
            except:
                return redirect(url_for('index'))

        return decorated
    return view_auth_decorator


def getBearerJwtPayload(bearer_jwt):
    print(bearer_jwt.replace('Bearer ', '').split('.')[1])
    print(base64.b64decode(bearer_jwt.replace(
        'Bearer ', '').split('.')[1] + '==').decode())
    return json.loads(str(base64.b64decode(bearer_jwt.replace('Bearer ', '').split('.')[1] + '==').decode()))


def config(app, test_config):

    app.config.from_mapping(
        SECRET_KEY='developmentsecretkey',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        SQLALCHEMY_DATABASE_URI='sqlite:///flask_app/database/database.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


def init_db(app):
    with app.app_context():
        db = get_db()
        with app.open_resource('./flask_app/database/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_PATH)
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv
