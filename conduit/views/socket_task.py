from functools import wraps

from flask import Blueprint
from flask import request

from conduit.extensions import socketio

bp = Blueprint("socket_task", __name__)

socketidLists = {}


def socket_checkid_wrapper(func):
    @wraps(func)
    def inside(*args, **kwargs):

        return func(*args, **kwargs)


@socketio.event
def set_socketid(data):
    new_str = f'user{data["userid"]}'
    socketidLists[new_str] = request.sid

    print("user socketid listed")


@socketio.event
def del_socketid(data):
    new_str = f'user{data["userid"]}'
    socketidLists.pop(new_str)

    print("user socket id removed")


@socketio.event
def send_doc(data):
    id_str = f'user{data["userid"]}'

    if id_str in socketidLists:
        socketio.emit("got_sent", data['docid'], to=socketidLists[id_str])


@socketio.on('connect')
def handle_connection():
    print('socket connected')