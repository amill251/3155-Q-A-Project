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
from flask_app.models.models import Answer, User, Question, AnswerVote, Vote, Report, PostReactions, Reactions


DATABASE_PATH = './flask_app/database/database.db'


def create_app(test_config=None):
    
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


def api_routes(app):
    
    @app.route("/api", methods=["GET", "POST"])
    @api_auth(app)
    def api():    

        return '',200

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

    

    @app.route("/api/questions", methods=["GET", "POST"])
    @api_auth(app)
    def questions():
        if request.method == "POST":
            
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
            bearer_token = request.headers['Authorization']
            user_id = getBearerJwtPayload(bearer_token)['user_id']
            
            
            if request.args.__contains__('question'):
                
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
                
                user_reported = Report.query.filter_by(user_id=user_id, question_id=questionId, answer_id=None).first()
                user_report = False

                if user_reported is not None:
                    user_report = True


                userReact = Reactions.query.join(PostReactions, PostReactions.reaction_id == Reactions.reaction_id).filter_by(user_id=user_id, question_id=questionId, answer_id=None).first()

                if userReact is None:
                    user_reaction = None
                else:
                    user_reaction = userReact.reaction_name   

                reactions = {
                    'like': PostReactions.query.filter_by(question_id=questionId, answer_id=None, reaction_id=1).count(),
                    'dislike': PostReactions.query.filter_by(question_id=questionId, answer_id=None, reaction_id=2).count(),
                    'cry': PostReactions.query.filter_by(question_id=questionId, answer_id=None, reaction_id=3).count(),
                    'angry': PostReactions.query.filter_by(question_id=questionId, answer_id=None, reaction_id=4).count(),
                    'laugh': PostReactions.query.filter_by(question_id=questionId, answer_id=None, reaction_id=5).count(),
                    'user_reaction': user_reaction
                }      

                question_dict = {
                    'question_id': question.question_id,
                    'user_id': question.user_id,
                    'title': question.title,
                    'contents': question.contents,
                    'date_created': question.date_created,
                    'username': user_name,
                    'user_reported': user_report,
                    'reactions': reactions
                }

                questions_response = dict()
                questions_response['data'] = []

                questions_response['data'].append(question_dict)

                response = jsonify(questions_response)

                return response

            elif request.args.__contains__('query'):

                queryString = request.args['query']

                search = "%{}%".format(queryString)

                fetched_questions = Question.query.filter(
                    Question.title.like(search)).all()

                questions_response = dict()
                questions_response['data'] = []

                for question in fetched_questions:
                    
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
                    questions_response['data'].append(question_dict)

                
                response = jsonify(questions_response)

                return response

            else:
                
                fetched_questions = db.session.query(Question).all()

                questions_response = dict()
                questions_response['data'] = []

                for question in fetched_questions:
                    
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
                    questions_response['data'].append(question_dict)

                
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
        

        if question.user_id is user_id:
            answers = db.session.query(Answer.answer_id).filter(Answer.question_id==delete_question_id).all()

            for answer in answers:
                db.session.query(AnswerVote).filter(AnswerVote.answer_id.in_(answer)).delete()

            Report.query.filter_by(question_id=delete_question_id).delete()
            PostReactions.query.filter_by(question_id=delete_question_id).delete()
            Answer.query.filter_by(question_id=delete_question_id).delete()
            Question.query.filter_by(question_id=delete_question_id).delete()

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

                userReact = Reactions.query.join(PostReactions, PostReactions.reaction_id == Reactions.reaction_id).filter_by(user_id=user_id, question_id=questionId, answer_id=answer.answer_id).first()

                if userReact is None:
                    user_reaction = None
                else:
                    user_reaction = userReact.reaction_name

                reactions = {
                    'like': PostReactions.query.filter_by(question_id=questionId, answer_id=answer.answer_id, reaction_id=1).count(),
                    'dislike': PostReactions.query.filter_by(question_id=questionId, answer_id=answer.answer_id, reaction_id=2).count(),
                    'cry': PostReactions.query.filter_by(question_id=questionId, answer_id=answer.answer_id, reaction_id=3).count(),
                    'angry': PostReactions.query.filter_by(question_id=questionId, answer_id=answer.answer_id, reaction_id=4).count(),
                    'laugh': PostReactions.query.filter_by(question_id=questionId, answer_id=answer.answer_id, reaction_id=5).count(),
                    'user_reaction': user_reaction
                }

                user_vote = 'novote'

                user_reported = Report.query.filter_by(user_id=user_id, answer_id=answer.answer_id).first()
                user_report = False

                if user_reported is not None:
                    user_report = True

                

                test_vote = Vote.query.join(AnswerVote, AnswerVote.vote_id == Vote.vote_id).filter_by(
                    answer_id=answer.answer_id, user_id=user_id).first()

                if test_vote is not None:
                    user_vote = test_vote.vote_name

                answer_dict = {
                    'answer_id': answer.answer_id,
                    'question_id': answer.question_id,
                    'user_id': answer.user_id,
                    'contents': answer.contents,
                    'date_created': answer.date_created,
                    'username': user_name,
                    'user_report': user_report,
                    'votes': {
                        'total_votes': total_votes['upvotes'] - total_votes['downvotes'],
                        'uservotes': user_vote
                    },
                    'reactions': reactions
                }

                answers_response['data'].append(answer_dict)

            response = jsonify(answers_response)

            return response

        return 0

    @app.route("/api/votes", methods=["GET", "POST"])
    @api_auth(app)
    def votes():
        
        if request.method == "POST":
            
            bearer_token = request.headers['Authorization']
            
            u_Id = getBearerJwtPayload(bearer_token)['user_id']
            
            a_Id = request.json['answer_id']
            
            vote_name = request.json['vote_name']
            
            try:
                current_vote = db.session.query(AnswerVote).filter_by(
                    user_id=u_Id, answer_id=a_Id).first()
            except Exception as e:
                print(e)
            current_vote = db.session.query(AnswerVote).filter_by(
                user_id=u_Id, answer_id=a_Id).first()

            
            current_vote_id = db.session.query(Vote).filter_by(
                vote_name=vote_name).one().vote_id
            
            if current_vote is None:
                
                new_record = AnswerVote(a_Id, u_Id, current_vote_id)      
                
                db.session.add(new_record)
                        
                try:
                    db.session.commit()
                except Exception as e:
                    print(e)
                
                return jsonify(success=True)
            elif current_vote.vote_id is current_vote_id:
                
                AnswerVote.query.filter_by(
                    user_id=u_Id, answer_id=a_Id).delete()
                db.session.commit()
                return jsonify(success=True)
            elif current_vote.vote_id is not current_vote_id:
                
                current_vote.vote_id = current_vote_id
                db.session.commit()
                return jsonify(success=True)
            return jsonify(success=False, message='Vote type not found')
        elif request.method == "GET":
            bearer_token = request.headers['Authorization']
            u_Id = getBearerJwtPayload(bearer_token)['user_id']
            q_Id = request.args['question']
            question_votes = db.session.query(AnswerVote).join(
                Answer, Answer.answer_id == AnswerVote.answer_id).filter_by(question_id=q_Id)
            votes_response = dict()
            votes_response['data'] = []
            for vote in question_votes:          
                vote_dict = {
                    'answer_id': vote.answer_id,
                    'user_id': vote.user_id,
                    'vote_id': vote.vote_id
                }

                votes_response['data'].append(vote_dict)

            return jsonify(votes_response)

        return 0

    @app.route("/api/report", methods=["GET", "POST"])
    @api_auth(app)
    def report():
        if request.method == "POST":
            bearer_token = request.headers['Authorization']
            u_Id = getBearerJwtPayload(bearer_token)['user_id']
            q_Id = request.json['question_id']
            a_Id = request.json['answer_id']
            current_report = db.session.query(Report).filter_by(
                user_id=u_Id, question_id=q_Id, answer_id=a_Id).first()
            if current_report is None:
                new_record = Report(u_Id, q_Id, a_Id)
                db.session.add(new_record)
                try:
                    db.session.commit()
                except Exception as e:
                    print(e)

                last_report = db.session.query(Report).filter_by(
                    question_id=q_Id, answer_id=a_Id).all()
                if len(last_report) >= 3:
                    if a_Id is None:
                        question = db.session.query(Question).filter_by(question_id=q_Id).first()
                        if not question:
                            return jsonify(succeed=False, message="Question not found"), 404

                        answers = db.session.query(Answer.answer_id).filter(Answer.question_id==q_Id).all()

                        for answer in answers:
                            db.session.query(AnswerVote).filter(AnswerVote.answer_id.in_(answer)).delete()

                        Report.query.filter_by(question_id=q_Id).delete()
                        PostReactions.query.filter_by(question_id=q_Id).delete()
                        Answer.query.filter_by(question_id=q_Id).delete()
                        Question.query.filter_by(question_id=q_Id).delete()      

                        db.session.commit()
                    else:
                        answers = db.session.query(Answer.answer_id).filter(Answer.answer_id==a_Id).first()
                        
                        db.session.query(AnswerVote).filter(AnswerVote.answer_id.in_(answers)).delete()
                        Report.query.filter_by(answer_id=a_Id).delete()
                        PostReactions.query.filter_by(answer_id=a_Id).delete()
                        Answer.query.filter_by(answer_id=a_Id).delete()

                        db.session.commit()
                return jsonify(success=True)
            elif current_report is not None:
                Report.query.filter_by(user_id=u_Id, question_id=q_Id, answer_id=a_Id).delete()
                db.session.commit()
                return jsonify(success=True)
            return jsonify(success=True)
        elif request.method == "GET":
            bearer_token = request.headers['Authorization']
            u_Id = getBearerJwtPayload(bearer_token)['user_id']
            
            reports = db.session.query(Report).all()
            reports_response = dict()
            reports_response['data'] = []
            for report in reports:
                report_dict = {
                    'user_id': report.user_id,
                    'question_id': report.question_id,
                    'answer_id': report.answer_id
                }
                reports_response['data'].append(report_dict)
            return jsonify(reports_response)
        return jsonify(success=True)
    
    @app.route("/api/reaction", methods=["GET", "POST"])
    @api_auth(app)
    def react():
        
        if request.method == "POST":
            
            bearer_token = request.headers['Authorization']
            u_Id = getBearerJwtPayload(bearer_token)['user_id']
            a_Id = request.json['answer_id']
            q_Id = request.json['question_id']
            r_name = request.json['reaction_name']
            current_reaction = db.session.query(PostReactions).filter_by(user_id=u_Id, answer_id=a_Id, question_id=q_Id).first()
            current_reaction_id = db.session.query(Reactions).filter_by(reaction_name=r_name).one().reaction_id
            
            if current_reaction is None:

                new_record = PostReactions(current_reaction_id, u_Id, q_Id, a_Id)
      
                db.session.add(new_record)
 
                try:
                    db.session.commit()
                except Exception as e:
                    print(e)
                
            elif current_reaction.reaction_id is current_reaction_id:
                
                PostReactions.query.filter_by(
                    user_id=u_Id, answer_id=a_Id, question_id=q_Id).delete()
                db.session.commit()
                return jsonify(success=True)
            elif current_reaction.reaction_id is not current_reaction_id:
                
                current_reaction.reaction_id = current_reaction_id
                db.session.commit()
                return jsonify(success=True)
            return jsonify(success=True)
        if request.method == "GET":
            reactions = db.session.query(PostReactions).all()
            reactions_response = dict()
            reactions_response['data'] = []
            for reaction in reactions:
                reaction_dict = {
                    'answer_id': reaction.answer_id,
                    'user_id': reaction.user_id,
                    'reaction_id': reaction.reaction_id,
                    'question_id': reaction.question_id
                }
                reactions_response['data'].append(reaction_dict)
            return jsonify(reactions_response)
        return jsonify(success=True)

def api_auth(app):
    def api_auth_decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):

            bearer_token = request.headers.get('Authorization')

            if not bearer_token:
                return jsonify({'message': 'Token is missing'}), 401
            
            if bool(re.search('^Bearer\s+(.*)', bearer_token)):
                token = bearer_token.replace('Bearer ', '')
            else:
                return jsonify({'message': 'Bearer Token is invalid'}), 401  

            try:
                jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
                
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
    
    return json.loads(str(base64.b64decode(bearer_jwt.replace('Bearer ', '').split('.')[1] + '==').decode()))


def config(app, test_config):

    app.config.from_mapping(
        SECRET_KEY='developmentsecretkey',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        SQLALCHEMY_DATABASE_URI='sqlite:///flask_app/database/database.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if test_config is None:
        
        app.config.from_pyfile('config.py', silent=True)
    else:
        
        app.config.from_mapping(test_config)

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
