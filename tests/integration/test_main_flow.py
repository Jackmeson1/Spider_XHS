import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from main import Data_Spider


def test_spider_note(monkeypatch):
    spider = Data_Spider()
    sample = {
        "data": {
            "items": [
                {
                    "id": "n1",
                    "url": "http://x.com/n1",
                    "note_card": {
                        "type": "normal",
                        "user": {
                            "user_id": "u1",
                            "nickname": "nick",
                            "avatar": "a.jpg",
                        },
                        "title": "title",
                        "desc": "desc",
                        "interact_info": {
                            "liked_count": 1,
                            "collected_count": 2,
                            "comment_count": 3,
                            "share_count": 4,
                        },
                        "image_list": [{"info_list": [{}, {"url": "img.jpg"}]}],
                        "tag_list": [{"name": "tag"}],
                        "time": 1609459200000,
                    },
                }
            ]
        }
    }

    def fake_get(note_url, cookies, proxies=None):
        return True, "ok", sample

    monkeypatch.setattr(spider.xhs_apis, "get_note_info", fake_get)
    success, msg, info = spider.spider_note("http://x.com/n1", "c")
    assert success
    assert info["note_id"] == "n1"
    assert info["note_type"] == "image_collection"
