import logging
import uuid

from flask import request, session
from unithon_nb import app, mongo3
from unithon_nb.util.trans import as_json, get_account
from json import loads
from bson.json_util import dumps

logger = logging.getLogger(__name__)


@app.route('/user/verify_sms/<user_name>/<cell_no>/', methods=['POST'])
@as_json
def verify_cell_phone(user_name, cell_no):
    return {
        'success': True,
        'result': {
            'verify_code': str(uuid.uuid4())
        }
    }


@app.route('/user/verify_sms/<verify_code>/', methods=['POST'])
@as_json
def verify_with_code(verify_code):
    req_json = request.get_json()

    try:
        if 'verify_number' not in req_json:
            raise RuntimeError('인증코드를 입력해주세요.')

        if req_json['verify_number'] == '123456':
            return {
                'success': True
            }
        else:
            raise RuntimeError('인증코드가 옳지 않습니다.')

    except Exception as ex:
        return {
            'success': False,
            'result': {
                'action': 'ERR0002',
                'msg': '에러가 발생했어요.\n에러 내용: %s' % str(ex)
            }

        }


@app.route('/user/', methods=['PUT', 'POST'])
@as_json
def user_login():
    req_json = request.get_json()

    try:
        if request.method == 'PUT':

            if 'type' not in req_json:
                raise RuntimeError('로그인 형식을 입력해주세요.')

            if 'name' not in req_json:
                raise RuntimeError('이름을 입력해주세요.')

            if 'cell_no' not in req_json:
                raise RuntimeError('휴대폰번호를 입력해주세요.')

            if req_json['type'] == 'kakao' or req_json['type'] == 'naver':
                if 'email' not in req_json:
                    raise RuntimeError('이메일을 입력해주세요.')
            else:
                if 'pw' not in req_json:
                    raise RuntimeError('비밀번호를 입력해주세요.')

            req_json['cell_no'] = req_json['cell_no'].replace('-', '').replace('+82', '0').strip()

            if mongo3.db.user.find({'cell_no': req_json['cell_no']}).count():
                raise RuntimeError('이미 존재하는 전화번호입니다.\n기존에 가입하신 방법으로 로그인해주세요.')

            result = mongo3.db.user.insert_one(req_json)

            session['name'] = req_json['name']
            session['cell_no'] = req_json['cell_no']
            session['id'] = str(result.inserted_id)

            return {
                'success': True,
                'session': get_account()
            }

        elif request.method == 'POST':
            session.clear()
            if session.get('name', False) and session.get('cell_no', False):
                return {
                    'success': True,
                    'session': get_account()
                }

            if 'type' not in req_json:
                raise RuntimeError('로그인 형식을 입력해주세요.')

            if req_json['type'] == 'kakao' or req_json['type'] == 'naver':
                if 'email' not in req_json:
                    raise RuntimeError('이메일을 입력해주세요.')
                else:
                    if mongo3.db.user.find({'email': req_json['email']}).count():
                        result = mongo3.db.user.find_one({'email': req_json['email']})
                        session['name'] = result['name']
                        session['cell_no'] = result['cell_no']
                        session['id'] = str(result['_id'])

                        return {
                            'success': True,
                            'session': get_account()
                        }
                    else:
                        return {
                            'success': False,
                            'msg': '회원 정보가 존재하지 않습니다.\n가입을 해주세요.'
                        }
            else:
                if 'cell_no' not in req_json:
                    raise RuntimeError('휴대폰번호를 입력해 주세요.')

                if 'pw' not in req_json:
                    raise RuntimeError('비밀번호를 입력해주세요.')

                req_json['cell_no'] = req_json['cell_no'].replace('-', '').replace('+82', '0').strip()

                if mongo3.db.user.find({'cell_no': req_json['cell_no'], 'pw': req_json['pw']}).count():
                    result = mongo3.db.user.find_one({'cell_no': req_json['cell_no'], 'pw': req_json['pw']})
                    session['name'] = result['name']
                    session['cell_no'] = result['cell_no']
                    session['id'] = str(result['_id'])

                    return {
                        'success': True,
                        'session': get_account()
                    }
                else:
                    return {
                        'success': False,
                        'action': 'ERR0002',
                        'msg': '회원 정보가 존재하지 않습니다.\n아이디와 비밀번호를 확인해주세요.'
                    }
    except Exception as ex:
        return {
            'success': False,
            'result': {
                'action': 'ERR0002',
                'msg': '에러가 발생했어요.\n에러 내용: %s' % str(ex)
            }

        }
