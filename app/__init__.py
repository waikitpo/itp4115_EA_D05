from flask import Flask
from jobsbd.route import index


app = Flask(__name__)

def create_app():
    app = Flask(__name__)
    app.add_url_rule('/', 'index', index)
    return app