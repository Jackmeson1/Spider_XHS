from typing import Tuple, List, Dict, Any
import requests
from xhs_utils.xhs_util import generate_request_params
from .base import BaseAPI


class FeedAPI(BaseAPI):
    def get_homefeed_all_channel(self, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, Any]:
        """Get all home feed channels"""
        res_json = None
        try:
            api = "/api/sns/web/v1/homefeed/category"
            headers, cookies, _ = generate_request_params(cookies_str, api)
            response = requests.get(self.base_url + api, headers=headers, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def get_homefeed_recommend(
        self,
        category: str,
        cursor_score: str,
        refresh_type: int,
        note_index: int,
        cookies_str: str,
        proxies: Dict[str, str] | None = None,
    ) -> Tuple[bool, str, Any]:
        """Get recommended notes for the home feed"""
        res_json = None
        try:
            api = "/api/sns/web/v1/homefeed"
            data = {
                "cursor_score": cursor_score,
                "num": 20,
                "refresh_type": refresh_type,
                "note_index": note_index,
                "unread_begin_note_id": "",
                "unread_end_note_id": "",
                "unread_note_count": 0,
                "category": category,
                "search_key": "",
                "need_num": 10,
                "image_formats": ["jpg", "webp", "avif"],
                "need_filter_image": False,
            }
            headers, cookies, trans_data = generate_request_params(cookies_str, api, data)
            response = requests.post(
                self.base_url + api,
                headers=headers,
                data=trans_data,
                cookies=cookies,
                proxies=proxies,
            )
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def get_homefeed_recommend_by_num(
        self,
        category: str,
        require_num: int,
        cookies_str: str,
        proxies: Dict[str, str] | None = None,
    ) -> Tuple[bool, str, List[Any]]:
        """Fetch a number of recommended notes from the home feed"""
        cursor_score, refresh_type, note_index = "", 1, 0
        note_list: List[Any] = []
        try:
            while True:
                success, msg, res_json = self.get_homefeed_recommend(
                    category,
                    cursor_score,
                    refresh_type,
                    note_index,
                    cookies_str,
                    proxies,
                )
                if not success:
                    raise Exception(msg)
                if "items" not in res_json["data"]:
                    break
                notes = res_json["data"]["items"]
                note_list.extend(notes)
                cursor_score = res_json["data"]["cursor_score"]
                refresh_type = 3
                note_index += 20
                if len(note_list) > require_num:
                    break
        except Exception as e:
            success, msg = False, str(e)
        if len(note_list) > require_num:
            note_list = note_list[:require_num]
        return success, msg, note_list
