import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import json
from freezegun import freeze_time

from xhs_utils import xhs_util


def test_signature_algorithm(monkeypatch):
    cookies_str = "a1=189d533c32bwp462awbnt4domm5ahdx406sgskfho50000420914"
    api = "/api/sns/web/v1/user_posted"
    data = {
        "num": "30",
        "cursor": "",
        "user_id": "63d276cb00000000110200a4",
        "image_formats": "jpg,webp,avif",
        "xsec_token": "AA",
        "xsec_source": "pc_search",
    }

    with freeze_time("2024-01-01 00:00:00"):
        xs, xt, xs_common = xhs_util.generate_xs_xs_common(
            cookies_str.split("=")[1], api, json.dumps(data, separators=(",", ":"))
        )

    def fake_generate(a1, api_in, data_in=""):
        assert a1 == cookies_str.split("=")[1]
        assert api_in == api
        return xs, xt, xs_common

    monkeypatch.setattr(xhs_util, "generate_xs_xs_common", fake_generate)
    headers, cookies, body = xhs_util.generate_request_params(cookies_str, api, data)

    assert headers["x-s"] == xs
    assert headers["x-s-common"] == xs_common
    assert headers["x-t"] == str(xt)
    assert cookies["a1"] == cookies_str.split("=")[1]
    assert json.loads(body) == data
