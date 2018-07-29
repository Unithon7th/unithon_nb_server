import logging
import datetime
import uuid

from flask import request, session
from unithon_nb import app, mongo3
from unithon_nb.util.trans import as_json, get_account
from json import loads
from bson.json_util import dumps, ObjectId


@app.route('/assets/reg/list/', methods=['GET'])
@as_json
def get_assets_list():
    return {
        'success': True,
        'result': loads(dumps(mongo3.db.env.find_one({'type': 'cate'}, {'_id': False, 'type': False})))
    }


@app.route('/assets/', methods=['PUT'])
@as_json
def save_assets():
    req_json = request.get_json()
    try:
        account = get_account()
        user_id = account.get('id', None)
        if user_id is None:
            raise RuntimeError('로그인을 해주세요.')

        if 'code' not in req_json:
            raise RuntimeError('카테고리 코드를 입력해주세요.')

        if 'amount' not in req_json:
            raise RuntimeError('자산의 양을 입력해주세요.')

        if 'complete' not in req_json:
            raise RuntimeError('재배 상태를 선택해주세요.')

        req_json['datetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        req_json['id'] = str(uuid.uuid4())

        result = mongo3.db.user.update_one({'_id': ObjectId(user_id)}, {'$push': {'assets': req_json}})

        live = []
        ns = []

        assets_result = mongo3.db.user.find_one({'_id': ObjectId(user_id)}, {'assets': True, '_id': False})
        for asset in assets_result.get('assets', None):
            is_live = False
            for item in ['beef', 'pork001', 'pork002', 'egg001', 'egg002', 'chicken']:
                if asset.get('code', None) == item:
                    is_live = True

            if is_live:
                live.append(asset)
            else:
                ns.append(asset)

        return {
            'success': True,
            'result': {
                'modified_count': result.modified_count,
                'matched_count': result.matched_count,
                'assets': {
                    'live': live,
                    'ns': ns
                }
            }
        }

    except Exception as ex:
        return {
            'success': False,
            'result': {
                'action': 'ERR0002',
                'msg': '에러가 발생했어요.\n에러 내용: %s' % str(ex)
            }

        }
