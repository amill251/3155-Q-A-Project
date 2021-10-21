import os

from flask import Flask, app, g
from flask import render_template
import sqlite3


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    DATABASE = './database/database.db'
    
    config(app, test_config)
    start_db(app, DATABASE)
    page_routes(app)
    api_routes(app)

    return app

def page_routes(app):
    #Routes for Pages
    @app.route("/")
    def index():
        return render_template("index.html")

def api_routes(app):
    #Routes for Pages
    @app.route("/api")
    def api():
        return 'Hello World'


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

def start_db(app, DATABASE):
    with app.app_context():
        db = get_db(DATABASE)
        with app.open_resource('./database/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db(DATABASE):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()