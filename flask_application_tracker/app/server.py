import os

from flask import Flask
from .auth.auth import auth_blueprint
from .emails.email_fetcher import email_fetcher_blueprint
from .db.mongo_manager import client

from flask_cors import CORS
# from application_tracker.email_test import fun
from dotenv import load_dotenv
load_dotenv()

def create_app(test_config=None):
    # create and configure the app
    # fun()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    CORS(app, resources={r"/*": {"origins": "*"}})
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

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(email_fetcher_blueprint, url_prefix='/email')

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app