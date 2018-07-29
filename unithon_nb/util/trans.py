import logging

from functools import wraps
from json import dumps

from flask import Response, session

logger = logging.getLogger(__name__)


def as_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        res = f(*args, **kwargs)
        res = dumps(res, ensure_ascii=False).encode('utf8')
        return Response(res, content_type='application/json; charset=utf-8',
                        headers={'Access-Control-Allow-Origin': 'http://localhost:8009 https://nb.ljh.app',
                                 'Access-Control-Allow-Credentials': 'true'})

    return decorated_function


def get_account():
    return {
        'name': session.get('name', None),
        'cell_no': session.get('cell_no', None),
        'id': session.get('id', None)
    }
