import logging
import datetime
import uuid
import pymongo

from flask import request, session
from unithon_nb import app, mongo3
from unithon_nb.util.trans import as_json, get_account
from json import loads
from bson.json_util import dumps, ObjectId


@app.route('/dashboard/', methods=['GET'])
@as_json
def get_dashboard():
    try:
        account = get_account()
        user_id = account.get('id', None)
        if user_id is None:
            raise RuntimeError('로그인을 해주세요.')

        item_price_trend = []
        now = datetime.datetime.now()
        assets_result = mongo3.db.user.find_one({'_id': ObjectId(user_id)},
                                                {'assets': True, 'tend_of_assets': True, '_id': False})
        item_m_per_prod = mongo3.db.env.find_one({'type': 'm_per_prod'})

        for asset in assets_result.get('assets', []):
            limit_2 = list(
                mongo3.db.daily_report.find({'code': asset['code']}, sort=[('time_stamp', pymongo.DESCENDING)]).limit(
                    2))
            if len(limit_2) == 2:
                item_price = {
                    'code': asset['code'],
                    'amount': asset['amount']
                }

                if asset['complete'] is True:
                    for item in item_m_per_prod['items']:
                        if item['code'] == asset['code']:
                            item_price['m_per_prod'] = item['m_per_prod']
                            item_price['complete'] = asset['complete']
                            item_price['name'] = item['name']
                            item_price['price'] = limit_2[0]['price'] * asset['amount']
                            item_price['prv_price'] = limit_2[1]['price'] * asset['amount']
                            item_price['gap_price'] = item_price['price'] - item_price['prv_price']
                else:
                    for item in item_m_per_prod['items']:
                        if item['code'] == asset['code']:
                            item_price['m_per_prod'] = item['m_per_prod']
                            item_price['complete'] = asset['complete']
                            item_price['name'] = item['name']
                            item_price['id'] = asset['id']
                            item_price['price'] = asset['amount'] * item['m_per_prod'] * limit_2[0]['price']
                            item_price['prv_price'] = asset['amount'] * item['m_per_prod'] * limit_2[1]['price']
                            item_price['gap_price'] = item_price['price'] - item_price['prv_price']
                            break
                item_price_trend.append(item_price)

        estimated_total_assets = 0
        live = []
        ns = []
        for asset in item_price_trend:
            is_live = False
            for item in ['beef', 'pork001', 'pork002', 'egg001', 'egg002', 'chicken']:
                if asset.get('code', None) == item:
                    is_live = True
            estimated_total_assets += asset['price']
            if is_live:
                live.append(asset)
            else:
                ns.append(asset)

        today = '%d-%02d-%02d' % (now.year, now.month, now.day)
        list_of_trends = assets_result.get('tend_of_assets', [])
        is_true = 0

        for idx, history_result in enumerate(list_of_trends):
            if history_result['date'] == today:
                is_true = idx
                break

        if is_true == 0:
            mongo3.db.user.update_one({'_id': ObjectId(user_id)},
                                      {'$set': {'tend_of_assets': [{
                                          'date': today,
                                          'price': estimated_total_assets
                                      }]}})
        return {
            'success': True,
            'result': {
                'assets': {
                    'estimated_total_assets': {
                        'amount': estimated_total_assets,
                        'type': 0 if len(live) == 0 else 1
                    },
                    'tend_of_assets': list_of_trends
                },
                'index': {
                    'live': live,
                    'ns': ns
                },
                'issue': {
                    'weather': {

                    },
                    'feed': [

                    ]
                }
            }
        }
    except Exception as ex:
        print(ex)
        return {
            'success': False,
            'result': {
                'action': 'ERR0002',
                'msg': '에러가 발생했어요.\n에러 내용: %s' % str(ex)
            }
        }
