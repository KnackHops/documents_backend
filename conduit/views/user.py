import random

from celery.result import AsyncResult

from flask import Blueprint
from flask import request
from flask import make_response

from conduit.wrapper import valid_wrapper
from conduit.wrapper import clean_id_wrapper
from conduit.wrapper import check_space_data_wrapper

from conduit.views.celery_task import send_email
from conduit.views.celery_task import password_attempt_timeout

from conduit import temp_db


bp = Blueprint("user", __name__)


bp = Blueprint("user", __name__)
user_data = temp_db.user_data
login_data = temp_db.login_data
user_pinned = temp_db.user_pinned
user_subordinate = temp_db.user_subordinate
user_email_unverified = temp_db.user_email_unverified

password_attempt = {}
password_attempt_timer = {}


@bp.route('/admin-fetch/')
@valid_wrapper
@check_space_data_wrapper
@clean_id_wrapper
def admin_fetch(id):
    # error = None
    # error_code = None
    global login_data
    global user_data
    global user_email_unverified

    if len(login_data) > 1:
        users = []

        for user in user_data:
            if not user['id'] == 0 and not user['id'] == id:
                for user_login in login_data:
                    if user_login['id'] == user['id']:
                        verified = True
                        attempt = None
                        resend = None
                        if len(user_email_unverified) > 0:
                            for user_ver in user_email_unverified:
                                if user_login['id'] == user_ver['userid']:
                                    verified = False
                                    attempt = user_ver['attempt']
                                    resend = user_ver['resend']
                        return_user = {
                            'id': user['id'],
                            'fullname': user['fullname'],
                            'username': user_login['username'],
                            'role': user['role'],
                            'activated': user['activated'],
                            'email_verified': verified,
                        }

                        if not verified:
                            return_user['attempt'] = attempt
                            return_user['resend'] = resend

                        users.append(return_user)

    else:
        users = None

    return make_response(({'fetched_users': users}, 200))


@bp.route('/subordinate-fetch/')
@valid_wrapper
@check_space_data_wrapper
@clean_id_wrapper
def friend_fetch(id):
    global login_data
    global user_data
    global user_subordinate

    if len(login_data) > 1:
        users = []
        for user_login in login_data:
            if not user_login['id'] == id:
                for user_sub in user_subordinate:
                    if user_sub['id'] == id:
                        if user_sub['subordinate_id'] == user_login['id']:
                            for user in user_data:
                                if user['id'] == user_login['id'] and user['activated']:
                                    users.append({
                                        'id': user_login['id'],
                                        'fullname': user['fullname'],
                                        'username': user_login['username'],
                                        'isSubordinate': True,
                                        'mobile': user['mobile'],
                                        'email': user['email']
                                    })

        for user_login in login_data:
            if not user_login['id'] == id:
                is_stranger = True
                activated = None

                for _user in users:
                    if _user['id'] == user_login['id']:
                        is_stranger = False
                if is_stranger:
                    for user in user_data:
                        if user['id'] == user_login['id'] and user['activated']:
                            users.append({
                                'id': user_login['id'],
                                'fullname': user['fullname'],
                                'username': user_login['username'],
                                'isSubordinate': False
                            })

    if len(users) == 0:
        users = None

    return make_response(({'fetched_users': users}, 200))


@bp.route('/send-user-fetch', methods=('GET', 'POST'))
@valid_wrapper
@check_space_data_wrapper
@clean_id_wrapper
def send_user_fetch(docid):
    if request.method == 'POST':
        id_lists = request.json['id_lists']
        global user_data
        global user_pinned

        if len(user_pinned) == 0:
            return make_response(({'id_filtered': id_lists}, 200))
        else:
            for each_pin in user_pinned:
                for id_user in id_lists:
                    if each_pin['userid'] == id_user['id'] and docid == each_pin['docid']:
                        id_user['pinned'] = True
            return_user = []
            for id_user in id_lists:
                if 'pinned' not in id_user:
                    return_user.append(id_user)

            return make_response(({'id_filtered': return_user}, 200))


@bp.route('/admin-check', methods=('GET', 'POST'))
@valid_wrapper
@check_space_data_wrapper
@clean_id_wrapper
def admin_check(id):
    if request.method == 'POST':
        error = 'Server Error'
        error_code = 500
        password = request.json['password']

        global user_data
        global login_data

        for user in user_data:
            if user['id'] == id:
                if not user['role'] == 'admin':
                    error_code = 409
                    error = "Not an admin!"

        if not error_code == 409:
            for user_login in login_data:
                if user_login['id'] == id:
                    if user_login['password'] == password:
                        return '', 204

        return {'error': error}, error_code


@bp.route('/admin-activate', methods=('GET', 'PUT'))
@valid_wrapper
@check_space_data_wrapper
@clean_id_wrapper
def admin_activate(id, userid):
    if request.method == 'PUT':
        error = None
        error_code = None

        global user_data
        global user_email_unverified

        for user in user_data:
            if id == user['id']:
                if not user['role'] == 'admin':
                    error_code = 409
                    error = 'User trying to activate another User is not an admin'

        if error_code:
            return {'error': error}, error_code
        else:
            is_verif = True
            if len(user_email_unverified) > 0:
                for user_verif in user_email_unverified:
                    if user_verif['userid'] == userid:
                        is_verif = False
            if is_verif:
                new_user_data = []
                for user in user_data:
                    upd_user = user
                    if userid == upd_user['id']:
                        upd_user['activated'] = not user['activated']
                    new_user_data.append(upd_user)

                user_data = new_user_data
                return '', 204
            else:
                new_user_data = []
                for user in user_data:
                    upd_user = user
                    if userid == upd_user['id']:
                        upd_user['role'] = 'normal'
                        upd_user['activated'] = False
                    new_user_data.append(upd_user)

                user_data = new_user_data

                return {'error': 'User is not verified!'}, 409


@bp.route('/admin-role-change', methods=('GET', 'PUT'))
@valid_wrapper
@check_space_data_wrapper
@clean_id_wrapper
def admin_role_change(id, userid):
    if request.method == 'PUT':
        error = None
        error_code = None
        role = request.json['role']
        global user_data

        for user in user_data:
            if id == user['id']:
                if not user['role'] == 'admin':
                    error_code = 409
                    error = 'User trying to activate another User is not an admin'

        if error_code:
            return {'error': error}, error_code
        else:
            new_user_data = []
            for user in user_data:
                if userid == user['id']:
                    user['role'] = role
                new_user_data.append(user)

            user_data = new_user_data

            return '', 204;


@bp.route('/login', methods=('GET', 'POST'))
@valid_wrapper
@check_space_data_wrapper
def login():
    if request.method == 'POST':
        # error = None
        # error_code = None
        id = None
        global login_data
        global user_data
        global user_email_unverified
        username = request.json['username']
        password = request.json['password']

        user_str = None
        for user_login in login_data:
            if user_login['username'] == username:
                user_str = f'user{username}'

                if user_str in password_attempt:
                    if password_attempt[user_str] < 10:
                        password_attempt[user_str] += 1
                    else:
                        if is_timer_done(user_str):
                            pass_reset_elapse(user_str)
                            password_attempt[user_str] = 1
                        else:
                            print("max attempt please wait")
                            return {'error': 'max attempt reached'}, 500
                else:
                    password_attempt[user_str] = 1

                if user_login['password'] == password:
                    id = user_login['id']

        if id or id == 0:
            pass_reset_elapse(user_str)
            return_user = {}

            if len(user_email_unverified) > 0:
                for user_unv in user_email_unverified:
                    if id == user_unv['userid']:
                        return_user['unverified'] = True

            if 'unverified' not in return_user:
                for user in user_data:
                    if id == user['id']:
                        if user['role'] == 'admin':
                            return_user = user
                        else:
                            if user['activated']:
                                return_user = user
                            else:
                                return_user['activated'] = False

            return_user['id'] = id
            return_user['username'] = username

            return make_response((return_user, 200))
        else:
            if user_str:
                print(password_attempt)
                print(password_attempt_timer)
                if password_attempt[user_str] == 10 and user_str not in password_attempt_timer:
                    uid = password_attempt_timeout.delay()
                    password_attempt_timer[user_str] = uid

            return {'error': 'Wrong password or Username'}, 500


def is_timer_done(userid):
    result = password_attempt_timer[userid]

    return result.ready()


@bp.route('/link-verify/')
@valid_wrapper
@check_space_data_wrapper
def link_verify():
    if request.method == 'GET':
        global user_email_unverified
        global login_data
        if len(user_email_unverified) > 0:
            username = request.args.get('username')
            # encrypt this dawg
            code = request.args.get('code')
            error = None

            userid = None
            for user in login_data:
                if user['username'] == username:
                    userid = user['id']

            if not userid and not userid == 0:
                return '<h1>User not found</h1>'

            new_user_list = []
            found = False

            for user_unverif in user_email_unverified:
                new_user = user_unverif
                if new_user['userid'] == userid:
                    found = True
                    if new_user['attempt'] < 3:
                        if not code == new_user['code']:
                            error = 'Code is incorrect!'
                            new_user['attempt'] = new_user['attempt'] + 1
                            new_user_list.append(new_user)
                    else:
                        error = "Reach the limit for verification attempt for this user"
                else:
                    new_user_list.append(user_unverif)

            if found:
                if error:
                    return f'<h1>{error}</h1>'
                else:
                    user_email_unverified = new_user_list
                    return f'<h1>User verified! ' \
                           f'Please wait for your account to be activated by and admin!\n' \
                           f'<a href="http://localhost:3000/landing-page">Visit the website</a></h1>'
            else:
                return "<h1>User already verified!<h1>"
        else:
            return "<h1>No unverified email</h1>"


@bp.route('/verify-user', methods=('GET', 'PUT'))
@valid_wrapper
@check_space_data_wrapper
@clean_id_wrapper
def verify_user(userid):
    if request.method == 'PUT':
        global user_email_unverified
        if len(user_email_unverified) > 0:
            error = None
            code = request.json['code']

            new_user_list = []
            for user_unverif in user_email_unverified:
                new_user = user_unverif
                if new_user['userid'] == userid:
                    if new_user['attempt'] < 3:
                        if not code == new_user['code']:
                            error = 'Code is incorrect!'
                            new_user['attempt'] = new_user['attempt'] + 1
                            new_user_list.append(new_user)
                    else:
                        error = "Reach the limit for verification attempt for this user"
                else:
                    new_user_list.append(user_unverif)

            user_email_unverified = new_user_list

            if error:
                return {'error': error}, 409
            else:
                return '', 204

        else:
            return {'error': 'No unverified email'}, 409


@bp.route('/resend-verification', methods=('GET', 'PUT'))
@valid_wrapper
@check_space_data_wrapper
@clean_id_wrapper
def resend_verification( userid ):
    if request.method == 'PUT':
        global user_email_unverified
        new_code = str(random.randint(1000, 9999))

        if len(user_email_unverified) > 0:
            new_user_list = []
            found = False
            error = None

            for user_unverif in user_email_unverified:
                new_user = user_unverif
                if new_user['userid'] == userid:
                    found = True
                    if new_user['resend'] < 3:
                        new_user['code'] = new_code
                        user_email = new_user['email']
                        username = new_user['username']
                        new_user['resend'] = new_user['resend'] + 1
                    else:
                        error = 'Reach resend limit of three for this user'

                new_user_list.append(new_user)

            if found:
                if error:
                    return {'error': error}, 409
                else:
                    send_email.delay(username, new_code, user_email)
                    return '', 204
            else:
                return {'error': 'User is verified!'}, 409

        else:
            return {'error': 'No unverified email'}, 409


@bp.route('/reset-user-verify-info', methods=('GET', 'PUT'))
@valid_wrapper
@check_space_data_wrapper
@clean_id_wrapper
def reset_user_attempt(userid):
    if request.method == 'PUT':
        which_change = request.json['which_change']

        if len(user_email_unverified) > 0:
            found = False
            for user_verif in user_email_unverified:
                if user_verif['userid'] == userid:
                    found = True
                    user_verif[which_change] = 0
            if found:
                return '', 204
            else:
                return {'error': 'user not found'}, 409
        else:
            return {'error': 'error resetting info'}, 409


@bp.route('/register', methods=('GET', 'POST'))
@valid_wrapper
@check_space_data_wrapper
def register():
    if request.method == 'POST':
        error = None
        error_code = None
        global login_data
        global user_data
        global user_email_unverified

        if login_data:
            for user_login in login_data:
                if user_login['username'] == request.json['username']:
                    error_code = 409
                    error = 'Username already exists!'

            for user in user_data:
                if user['email'] == request.json['email']:
                    error_code = 409
                    error = 'Email already exists!'
                if user['mobile'] == request.json['mobile']:
                    error_code = 409
                    error = 'Mobile number already exists'

        if not error_code:
            id = login_data[-1]['id'] + 1

            new_user_login = {
                'id': id,
                'username': request.json['username'],
                'password': request.json['password']
            }

            new_user = {
                'id': id,
                'fullname': request.json['fullname'],
                'email': request.json['email'],
                'mobile': request.json['mobile'],
                'role': "normal",
                'activated': False
            }

            new_code = str(random.randint(1000, 9999))

            new_unverified = {
                'userid': id,
                'username': request.json['username'],
                'email': request.json['email'],
                'code': new_code,
                'attempt': 0,
                'resend': 0
            }

            login_data.append(new_user_login)
            user_data.append(new_user)
            user_email_unverified.append(new_unverified)

            send_email.delay(request.json['username'], new_code, request.json['email'])

            return make_response(({'id': id, 'username': request.json['username']}, 200))

        if error_code:
            return {'error': error}, error_code


@bp.route('/admin-delete-user/', methods=('GET', 'DELETE'))
@valid_wrapper
@check_space_data_wrapper
@clean_id_wrapper
def admin_delete_user(id, userid):
    if request.method == 'DELETE':
        error = None
        error_code = None
        global user_data
        global login_data
        global user_email_unverified
        global user_subordinate
        global user_pinned

        if id == 0 != userid:
            new_user_data = []
            for user in user_data:
                if user['id'] != userid:
                    new_user_data.append(user)

            new_login_data = []
            for user_login in login_data:
                if user_login['id'] != userid:
                    new_login_data.append(user_login)

            new_user_verif = []
            for user_verif in user_email_unverified:
                if user_verif['userid'] != userid:
                    new_user_verif.append(user_verif)

            new_user_pin = []
            for each_pin in user_pinned:
                if each_pin['userid'] != userid:
                    new_user_pin.append(each_pin)

            new_user_sub = []
            for user_sub in user_subordinate:
                if not (user_sub['id'] == userid) and not (user_sub['subordinate_id'] == userid):
                    new_user_sub.append(user_sub)

            user_data = new_user_data
            login_data = new_login_data
            user_email_unverified = new_user_verif
            user_subordinate = new_user_sub
        else:
            error = 'You are trying to delete yourself!'
            error_code = 409

        if error:
            return {'error': error}, error_code
        else:
            return '', 204


@bp.route('/add-subordinate', methods=('GET', 'PUT'))
@valid_wrapper
@check_space_data_wrapper
@clean_id_wrapper
def add_subordinate(id, userid):
    if request.method == 'PUT':
        global user_subordinate
        global user_data

        for user_sub in user_subordinate:
            if user_sub['id'] == id and userid == user_sub['subordinate_id']:
                return {'error': 'already a subordinate!'}, 409

        for user in user_data:
            if (user['id'] == id or user['id'] == userid) and not user['activated']:
                return {'error': 'user not activated!'}, 409

        user_subordinate.append({
            'id': id,
            'subordinate_id': userid
        })

        return '', 204


@bp.route('/remove-subordinate/', methods=('GET', 'DELETE'))
@valid_wrapper
@check_space_data_wrapper
@clean_id_wrapper
def remove_subordinate(id, userid):
    if request.method == 'DELETE':
        global user_data
        global user_subordinate

        for user in user_data:
            if (user['id'] == id or user['id'] == userid) and not user['activated']:
                return {'error': 'user not activated!'}, 409

        found = False
        new_sub = []
        for user_sub in user_subordinate:
            if user_sub['id'] == id and user_sub['subordinate_id'] == userid:
                found = True
            else:
                new_sub.append(user_sub)

        if found:
            user_subordinate = new_sub
            return '', 204
        else:
            return {'error': 'not a subordinate in the first place'}, 409


@bp.route('/update-user', methods=('GET', 'PUT'))
@valid_wrapper
@check_space_data_wrapper
@clean_id_wrapper
def update_user(userid):
    if request.method == 'PUT':
        val = request.json['val']
        which = request.json['which']
        global user_data

        if len(user_data) > 0:

            for user in user_data:
                if user[which] == val:
                    return {'error': f'This {which} is already being used!'}, 409

            _update_user_data = []

            for user in user_data:
                each_user = user
                if user['id'] == userid:
                    each_user[which] = val

                _update_user_data.append(each_user)

            user_data = _update_user_data
            return '', 204
        else:
            return {'error': 'no user detected'}, 409


def pass_reset_elapse(user_str):
    if password_attempt[user_str]:
        del (password_attempt[user_str])
        if user_str in password_attempt_timer:
            del (password_attempt_timer[user_str])

