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
from flask_app.models.models import User as User
from flask_app.models.models import Question as Question

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
       
        response = jsonify(succeed=True, message='User ' + str(_uname) + ' created successfully')
        token_expires = 3600
        bearer_token = 'Bearer ' + jwt.encode({'user': _uname, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=token_expires), 'expires_in': token_expires}, app.config['SECRET_KEY'], algorithm="HS256")

        response = jsonify(succeed=True, message='User ' + str(_uname) + ' logged in successfully')
        base64_encoded_bearer = str(base64.b64encode(str.encode(bearer_token)).decode())
        response.set_cookie('bt' , base64_encoded_bearer, httponly = True)
        response.set_cookie('exp', str(getBearerJwtPayload(bearer_token)['exp']))
        response.set_cookie('expires_in', str(getBearerJwtPayload(bearer_token)['expires_in']))
        response.set_cookie('user', str(getBearerJwtPayload(bearer_token)['user']))

        return response


    @app.route("/api/users/login", methods=["POST"])
    def login_user():

        _uname = request.json['_username']
        _pword = request.json['_password']

        fetched_user = db.session.query(User).filter_by(_username=_uname).first()
        

        if not fetched_user:
            return jsonify(succeed=False, message='User not found')

        hash_pass = bytes(str(_pword), 'utf-8')
        secret = bytes(app.config['SECRET_KEY'], 'utf-8')

        signature = str(base64.b64encode(
            hmac.new(secret, hash_pass, digestmod=hashlib.sha256).digest()).decode())


        if fetched_user._password == signature:
            token_expires = 3600
            bearer_token = 'Bearer ' + jwt.encode({'user': _uname, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=token_expires), 'expires_in': token_expires}, app.config['SECRET_KEY'], algorithm="HS256")

            response = jsonify(succeed=True, message='User ' + str(_uname) + ' logged in successfully')
            base64_encoded_bearer = str(base64.b64encode(str.encode(bearer_token)).decode())
            response.set_cookie('bt' , base64_encoded_bearer, httponly = True)
            response.set_cookie('exp', str(getBearerJwtPayload(bearer_token)['exp']))
            response.set_cookie('expires_in', str(getBearerJwtPayload(bearer_token)['expires_in']))
            response.set_cookie('user', str(getBearerJwtPayload(bearer_token)['user']))
            return response
        else:
            return jsonify(succeed=False, message='Incorrect Password')



    @app.route("/api/refresh-token", methods=["GET"])
    @cookie_auth(app)
    def refresh_token():

        cookie_token = request.cookies.get('bt')

        bearer_token = str(base64.b64decode(cookie_token).decode())
        token_expires = 360000

        bearer_token = 'Bearer ' + jwt.encode({'user': getBearerJwtPayload(bearer_token)['user'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=token_expires), 'expires_in': token_expires}, app.config['SECRET_KEY'], algorithm="HS256")
        
        base64_encoded_bearer = str(base64.b64encode(str.encode(bearer_token)).decode())

        response = jsonify(token=bearer_token)
        response.set_cookie('bt' , base64_encoded_bearer, httponly = True)
        response.set_cookie('exp', str(getBearerJwtPayload(bearer_token)['exp']))
        response.set_cookie('expires_in', str(getBearerJwtPayload(bearer_token)['expires_in']))

        response.set_cookie('user', str(getBearerJwtPayload(bearer_token)['user']))

        return response


    # Questions Questions Questions Questions Questions Questions Questions Questions
    @app.route("/api/questions", methods=["GET", "POST"])
    @api_auth(app)
    def questions():
        print('Question was called')
        if request.method == "POST":
            print(request.json)
            u_id = request.json['user_id']
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

                question = db.session.query(Question).filter_by(question_id=questionId).first()

                question_dict = {
                        'question_id': question.question_id,
                        'user_id': question.user_id,
                        'title': question.title,
                        'contents': question.contents,
                        'date_created': question.date_created
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
                    question_dict = {
                        'question_id': question.question_id,
                        'user_id': question.user_id,
                        'title': question.title,
                        'contents': question.contents,
                        'date_created': question.date_created
                    }
                    questions_response['data'].append(question_dict)

                response = jsonify(questions_response)

                return response

def api_auth(app):
    def api_auth_decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):

            bearer_token = request.headers.get('Authorization')

            print(bearer_token)

            if not bearer_token:
                return jsonify({'message' : 'Token is missing'}), 401
            print('Past 1')
            if bool(re.search('^Bearer\s+(.*)', bearer_token)):
                token = bearer_token.replace('Bearer ', '')
            else:
                return jsonify({'message' : 'Bearer Token is invalid'}), 401
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
    print(base64.b64decode(bearer_jwt.replace('Bearer ', '').split('.')[1] + '==').decode())
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
