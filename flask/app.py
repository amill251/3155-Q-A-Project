import os

from flask import Flask, app, g
from flask import render_template
import sqlite3


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    config(app, test_config)
    page_routes(app)
    api_routes(app)

    return app


def page_routes(app):
    # Routes for Pages
    @app.route("/")
    def index():
        return render_template("createaccount.html")

    # No idea if this works but I added a way to get to the login screen -Neal
# def page_routes(app):
    # Routes for sign in insted
    # @app.route("/login")
    # def index():
        # return render_template("login.html")


def api_routes(app):
    # Routes for Pages
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
