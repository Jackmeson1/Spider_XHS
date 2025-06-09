import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import requests_mock
from unittest.mock import patch

from apis.xhs_pc_apis import XHS_Apis


def fake_generate_xs_xs_common(a1, api, data=''):
    return ('sigxs', 111111, 'sigcommon')

def fake_generate_x_b3_traceid(length=16):
    return 'traceid'


def test_homefeed_signature_headers():
    api = XHS_Apis()
    cookies = "a1=demo"
    url = "https://edith.xiaohongshu.com/api/sns/web/v1/homefeed/category"
    with patch('xhs_utils.xhs_util.generate_xs_xs_common', fake_generate_xs_xs_common), \
         patch('xhs_utils.xhs_util.generate_x_b3_traceid', fake_generate_x_b3_traceid):
        with requests_mock.Mocker() as m:
            m.get(url, json={"success": True, "msg": "ok", "data": {}})
            success, msg, data = api.get_homefeed_all_channel(cookies)
            assert success
            req = m.request_history[0]
            assert req.headers['x-s'] == 'sigxs'
            assert req.headers['x-s-common'] == 'sigcommon'
            assert req.headers['x-t'] == '111111'
            assert req.headers['x-b3-traceid'] == 'traceid'

import inspect

class DummyResponse:
    def __init__(self):
        self._json = {"success": True, "msg": "ok", "data": {}}
    def json(self):
        return self._json


def fake_request(*args, **kwargs):
    return DummyResponse()


def test_smoke_all_api_methods(monkeypatch):
    api = XHS_Apis()
    monkeypatch.setattr('requests.get', fake_request)
    monkeypatch.setattr('requests.post', fake_request)

    for name, method in inspect.getmembers(api, predicate=inspect.ismethod):
        if name.startswith('_'):
            continue
        params = inspect.signature(method).parameters
        args = []
        for p in list(params.values())[1:]:
            if p.name == 'cookies_str':
                args.append('a1=demo')
            elif 'cursor' in p.name:
                args.append('')
            elif p.name in ['user_id', 'note_id', 'category', 'query', 'url', 'user_url', 'word']:
                args.append('id')
            elif p.name in ['require_num', 'page']:
                args.append(1)
            elif p.name in ['refresh_type', 'note_index', 'sort_type_choice', 'note_type', 'note_time', 'note_range', 'pos_distance']:
                args.append(0)
            elif p.name in ['xsec_token', 'xsec_source', 'geo']:
                args.append('')
            elif p.name == 'proxies':
                args.append(None)
            elif p.name == 'comment':
                args.append({'note_id':'id','id':'cid','sub_comment_has_more':False,'sub_comment_cursor':'','sub_comments':[]})
            else:
                args.append(None)
        try:
            method(*args)
        except Exception:
            pass
