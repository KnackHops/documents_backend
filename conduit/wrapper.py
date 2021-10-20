from functools import wraps
from flask import request


def clean_id_wrapper(func):
    @wraps(func)
    def inside(*args, **kwargs):
        if request.args:
            data = request.args.to_dict()
        else:
            data = request.json

        checked_id = id_check(data)

        if checked_id:
            return func(*args, **kwargs, **checked_id)

        return {"error": "missing values"}, 400

    return inside


def id_check(data):
    key_list_id = ['userid', 'id', 'docid']

    return_list_id = {}

    for key in data:
        if key in key_list_id:
            try:
                return_list_id[key] = int(data[key])
            except ValueError:
                return False

    return return_list_id


def check_space_data_wrapper(func):
    @wraps(func)
    def inside(*args, **kwargs):
        if request.args:
            data = request.args.to_dict()
        else:
            data = request.json

        space_protocol_alert = check_key_space(data)

        if space_protocol_alert:
            return {"error": f"Invalid whitespace in {space_protocol_alert}"}

        return func(*args, **kwargs)
    return inside


def check_key_space(data):
    key_lists = ["email", "username", "password", "id", "userid", "mobile", "role", "docid", "code"]

    for key in data:
        if key in key_lists:
            if not type(data[key]) == int:
                if " " in data[key]:
                    return key

    return False


def valid_wrapper(func):
    @wraps(func)
    def inside(*args, **kwargs):
        if not request.path == "/":

            if len(request.args) > 0:
                data = request.args.to_dict()
            elif request.json:
                data = request.json
            else:
                return {'error': 'no data'}, 400

            check_return = validity_check(data)

            if check_return:
                return check_return

        return func(*args, **kwargs)
    return inside


def validity_check(list_req):
    for key in list_req:
        val = list_req[key]
        if not val and not val == 0:
            return {'error': f'{key} is empty'}, 400

    return None


