from conduit.app import create_app
from conduit.app import celery

from conduit.celery_app import init_celery

from conduit.extensions import socketio

from flask import request

app = create_app()
init_celery(celery, app)


@app.route('/')
def index():
    return f'<h1>Hi! You are accessing my root! ' \
            f'<a href="https://github.com/KnackHops/documents_backend">' \
            f'Here is the link for the api!</a> <h1>'


@app.after_request
def after_request_func(response):
    if not request.path == "/" and not request.path == '/link-verify/' and not request.path == '/test-celery-task':
        response.headers['Content-Type'] = 'application/json'

    return response


if __name__ == "__main__":
    socketio.run(app, debug=True)