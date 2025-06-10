from typing import Tuple, List, Dict, Any
import json
import urllib
from xhs_utils.xhs_util import splice_str, generate_request_params, generate_x_b3_traceid
from .base import BaseAPI

SORT_MAP = {
    1: "time_descending",
    2: "popularity_descending",
    3: "comment_descending",
    4: "collect_descending",
}
NOTE_TYPE_MAP = {1: "视频笔记", 2: "普通笔记"}
NOTE_TIME_MAP = {1: "一天内", 2: "一周内", 3: "半年内"}
NOTE_RANGE_MAP = {1: "已看过", 2: "未看过", 3: "已关注"}
POS_DISTANCE_MAP = {1: "同城", 2: "附近"}


def _build_filters(
    sort_choice: int, note_type: int, note_time: int, note_range: int, pos_distance: int
) -> List[Dict[str, Any]]:
    return [
        {"tags": [SORT_MAP.get(sort_choice, "general")], "type": "sort_type"},
        {"tags": [NOTE_TYPE_MAP.get(note_type, "不限")], "type": "filter_note_type"},
        {"tags": [NOTE_TIME_MAP.get(note_time, "不限")], "type": "filter_note_time"},
        {"tags": [NOTE_RANGE_MAP.get(note_range, "不限")], "type": "filter_note_range"},
        {"tags": [POS_DISTANCE_MAP.get(pos_distance, "不限")], "type": "filter_pos_distance"},
    ]


class SearchAPI(BaseAPI):
    def get_search_keyword(self, word: str, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, Any]:
        """Fetch search suggestions"""
        res_json = None
        try:
            api = "/api/sns/web/v1/search/recommend"
            params = {"keyword": urllib.parse.quote(word)}
            splice_api = splice_str(api, params)
            headers, cookies, _ = generate_request_params(cookies_str, splice_api)
            response = self._get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def search_note(
        self,
        query: str,
        cookies_str: str,
        page: int = 1,
        sort_type_choice: int = 0,
        note_type: int = 0,
        note_time: int = 0,
        note_range: int = 0,
        pos_distance: int = 0,
        geo: str | dict = "",
        proxies: Dict[str, str] | None = None,
    ) -> Tuple[bool, str, Any]:
        """Search notes"""
        res_json = None
        filters = _build_filters(sort_type_choice, note_type, note_time, note_range, pos_distance)
        if geo:
            geo = json.dumps(geo, separators=(",", ":"))
        try:
            api = "/api/sns/web/v1/search/notes"
            data = {
                "keyword": query,
                "page": page,
                "page_size": 20,
                "search_id": generate_x_b3_traceid(21),
                "sort": "general",
                "note_type": 0,
                "ext_flags": [],
                "filters": filters,
                "geo": geo,
                "image_formats": ["jpg", "webp", "avif"],
            }
            headers, cookies, data = generate_request_params(cookies_str, api, data)
            response = self._post(
                self.base_url + api,
                headers=headers,
                data=data.encode("utf-8"),
                cookies=cookies,
                proxies=proxies,
            )
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def search_some_note(
        self,
        query: str,
        require_num: int,
        cookies_str: str,
        sort_type_choice: int = 0,
        note_type: int = 0,
        note_time: int = 0,
        note_range: int = 0,
        pos_distance: int = 0,
        geo: str | dict = "",
        proxies: Dict[str, str] | None = None,
    ) -> Tuple[bool, str, List[Any]]:
        """Search a fixed number of notes"""
        page = 1
        note_list: List[Any] = []
        try:
            while True:
                success, msg, res_json = self.search_note(
                    query,
                    cookies_str,
                    page,
                    sort_type_choice,
                    note_type,
                    note_time,
                    note_range,
                    pos_distance,
                    geo,
                    proxies,
                )
                if not success:
                    raise Exception(msg)
                if "items" not in res_json["data"]:
                    break
                notes = res_json["data"]["items"]
                note_list.extend(notes)
                page += 1
                if len(note_list) >= require_num or not res_json["data"]["has_more"]:
                    break
        except Exception as e:
            success, msg = False, str(e)
        if len(note_list) > require_num:
            note_list = note_list[:require_num]
        return success, msg, note_list

    def search_user(self, query: str, cookies_str: str, page: int = 1, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, Any]:
        """Search users"""
        res_json = None
        try:
            api = "/api/sns/web/v1/search/usersearch"
            data = {
                "search_user_request": {
                    "keyword": query,
                    "search_id": "2dn9they1jbjxwawlo4xd",
                    "page": page,
                    "page_size": 15,
                    "biz_type": "web_search_user",
                    "request_id": "22471139-1723999898524",
                }
            }
            headers, cookies, data = generate_request_params(cookies_str, api, data)
            response = self._post(
                self.base_url + api,
                headers=headers,
                data=data.encode("utf-8"),
                cookies=cookies,
                proxies=proxies,
            )
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def search_some_user(
        self,
        query: str,
        require_num: int,
        cookies_str: str,
        proxies: Dict[str, str] | None = None,
    ) -> Tuple[bool, str, List[Any]]:
        """Search a fixed number of users"""
        page = 1
        user_list: List[Any] = []
        try:
            while True:
                success, msg, res_json = self.search_user(query, cookies_str, page, proxies)
                if not success:
                    raise Exception(msg)
                if "users" not in res_json["data"]:
                    break
                users = res_json["data"]["users"]
                user_list.extend(users)
                page += 1
                if len(user_list) >= require_num or not res_json["data"]["has_more"]:
                    break
        except Exception as e:
            success, msg = False, str(e)
        if len(user_list) > require_num:
            user_list = user_list[:require_num]
        return success, msg, user_list
