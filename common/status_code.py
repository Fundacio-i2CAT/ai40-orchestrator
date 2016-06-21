from flask import jsonify


def not_found(service_id):
    message = {
            'status': 404,
            'message': 'Not Found: ' + service_id
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


def action_error(service_id):
    message = {
        'status': 400,
        'message': 'Bad request:  ' + service_id
    }
    resp = jsonify(message)
    resp.status_code = 400
    return resp


def is_ok_no_content():
    message = {
        'status': 204
    }
    resp = jsonify(message)
    resp.status_code = 204
    return resp


