import os
import json

from flask import Flask, app, g, request, jsonify
from flask import render_template
import sqlite3
DATABASE_PATH = './database/database.db'

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    config(app, test_config)
    init_db(app)
    page_routes(app)
    api_routes(app)

    return app

def page_routes(app):
    #Routes for Pages
    @app.route("/")
    def index():
        return render_template("createaccount.html")

def api_routes(app):
    #Routes for Pages
    @app.route("/api", methods=["GET", "POST"])
    def api():
        #this is a placeholder for testing
        return 'Okay'

    @app.route("/api/usercreate", methods=["GET", "POST"])
    def usercreate():
        u_id = request.json['user_id']
        f_name = request.json['first_name']
        l_name = request.json['last_name']
        _uname = request.json['_username']
        _pword = request.json['_password']
        
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        
        cur.execute("INSERT INTO users (user_id,first_name,last_name,_username,_password) VALUES (?,?,?,?,?)", (u_id,f_name,l_name,_uname,_pword))
        
        con.commit()
        con.close()
        return jsonify(response='Success')

    @app.route("/api/getusers", methods=["GET", "POST"])
    def getusers():
        con = sqlite3.connect(DATABASE_PATH)
        # con.row_factory = sqlite3.Row
        
        cur = con.cursor()
        cur.execute("select * from users")
        
        rows = cur.fetchall()
        con.close()
        return jsonify(data=rows)


def config(app, test_config):
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
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
        with app.open_resource('./database/schema.sql', mode='r') as f:
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