from flask import Flask
from container import Container


def create_app():
    container = Container()
    flask_app = Flask(__name__)
    flask_app.container = container
    flask_app.register_blueprint()