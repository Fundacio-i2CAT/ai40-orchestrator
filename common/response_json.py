from flask import jsonify


def not_found(message):
    message = {
            'status': 404,
            'message': message
    }
    resp = jsonify(message)
    resp.status_code = 404
    construct_headers(resp)
    return resp


def action_error(service_id):
    message = {
        'status': 400,
        'message': 'Bad request:  ' + service_id
    }
    resp = jsonify(message)
    resp.status_code = 400
    construct_headers(resp)
    return resp


def connect_vm_error(e):
    message = {
        'status': 500,
        'message': e
    }
    resp = jsonify(message)
    resp.status_code = 500
    construct_headers(resp)
    return resp

def is_ok_no_content():
    message = {
        'status': 204
    }
    resp = jsonify(message)
    resp.status_code = 204
    construct_headers(resp)
    return resp


def construct_headers(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp
