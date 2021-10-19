import os
from flask import Flask

from conduit.extensions import cors
from conduit.extensions import socketio

from instance.config import DevelopmentConfigLocalHost


def create_app(config=None):

    app = Flask(__name__.split(".")[0], instance_relative_config=True)
    create_folders(app)
    app.config.from_object(DevelopmentConfigLocalHost)

    attach_extensions(app)
    attach_blueprints(app)

    return app


def attach_extensions(app):
    cors.init_app(app, origins="*")
    socketio.init_app(app, cors_allowed_origins="*")


def attach_blueprints(app):
    from conduit.views import user
    from conduit.views import document
    from conduit.views import socket_task

    app.register_blueprint(user.bp)
    app.register_blueprint(document.bp)
    app.register_blueprint(socket_task.bp)


def create_folders(app):
    env = os.environ.get("ENVIRONMENT", "DEVELOPMENT")

    if env == "DEVELOPMENT":
        try:
            os.mkdir(app.instance_path)
        except OSError:
            pass