from flask import Flask
from app.route import index, login
from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.add_url_rule('/index', 'index', index)
    app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
    return app