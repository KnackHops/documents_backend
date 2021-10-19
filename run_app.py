from conduit.app import create_app
from conduit.extensions import socketio

app = create_app()


@app.route('/')
def index():
    return f'<h1>Hi! You are accessing my root! ' \
            f'<a href="https://github.com/KnackHops/documents_backend">' \
            f'Here is the link for the api!</a> <h1>'


if __name__ == "__main__":
    socketio.run(app, debug=True)