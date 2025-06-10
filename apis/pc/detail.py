from __future__ import annotations
from typing import Tuple, List, Dict, Any
import urllib
import re
from xhs_utils.xhs_util import splice_str, generate_request_params, get_common_headers
from .base import BaseAPI


class DetailAPI(BaseAPI):
    def get_user_info(self, user_id: str, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, Any]:
        """Get information for a user"""
        res_json = None
        try:
            api = "/api/sns/web/v1/user/otherinfo"
            params = {"target_user_id": user_id}
            splice_api = splice_str(api, params)
            headers, cookies, _ = generate_request_params(cookies_str, splice_api)
            response = self._get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def get_user_self_info(self, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, Any]:
        """Get the authenticated user's info"""
        res_json = None
        try:
            api = "/api/sns/web/v1/user/selfinfo"
            headers, cookies, _ = generate_request_params(cookies_str, api)
            response = self._get(self.base_url + api, headers=headers, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def get_user_self_info2(self, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, Any]:
        """Get the authenticated user's info (v2)"""
        res_json = None
        try:
            api = "/api/sns/web/v2/user/me"
            headers, cookies, _ = generate_request_params(cookies_str, api)
            response = self._get(self.base_url + api, headers=headers, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def get_user_note_info(
        self,
        user_id: str,
        cursor: str,
        cookies_str: str,
        xsec_token: str = "",
        xsec_source: str = "",
        proxies: Dict[str, str] | None = None,
    ) -> Tuple[bool, str, Any]:
        """Fetch user notes at a cursor"""
        res_json = None
        try:
            api = "/api/sns/web/v1/user_posted"
            params = {
                "num": "30",
                "cursor": cursor,
                "user_id": user_id,
                "image_formats": "jpg,webp,avif",
                "xsec_token": xsec_token,
                "xsec_source": xsec_source,
            }
            splice_api = splice_str(api, params)
            headers, cookies, _ = generate_request_params(cookies_str, splice_api)
            response = self._get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def get_user_all_notes(self, user_url: str, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, List[Any]]:
        """Fetch all notes for a user"""
        cursor = ""
        note_list: List[Any] = []
        try:
            url_parse = urllib.parse.urlparse(user_url)
            user_id = url_parse.path.split("/")[-1]
            kv_dist = {kv.split("=")[0]: kv.split("=")[1] for kv in url_parse.query.split("&")}
            xsec_token = kv_dist.get("xsec_token", "")
            xsec_source = kv_dist.get("xsec_source", "pc_search")
            while True:
                success, msg, res_json = self.get_user_note_info(user_id, cursor, cookies_str, xsec_token, xsec_source, proxies)
                if not success:
                    raise Exception(msg)
                notes = res_json["data"]["notes"]
                cursor = str(res_json["data"].get("cursor", ""))
                note_list.extend(notes)
                if len(notes) == 0 or not res_json["data"].get("has_more", False):
                    break
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, note_list

    def get_user_like_note_info(
        self,
        user_id: str,
        cursor: str,
        cookies_str: str,
        xsec_token: str = "",
        xsec_source: str = "",
        proxies: Dict[str, str] | None = None,
    ) -> Tuple[bool, str, Any]:
        """Fetch liked notes at a cursor"""
        res_json = None
        try:
            api = "/api/sns/web/v1/note/like/page"
            params = {
                "num": "30",
                "cursor": cursor,
                "user_id": user_id,
                "image_formats": "jpg,webp,avif",
                "xsec_token": xsec_token,
                "xsec_source": xsec_source,
            }
            splice_api = splice_str(api, params)
            headers, cookies, _ = generate_request_params(cookies_str, splice_api)
            response = self._get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def get_user_all_like_note_info(self, user_url: str, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, List[Any]]:
        """Fetch all liked notes for a user"""
        cursor = ""
        note_list: List[Any] = []
        try:
            url_parse = urllib.parse.urlparse(user_url)
            user_id = url_parse.path.split("/")[-1]
            kv_dist = {kv.split("=")[0]: kv.split("=")[1] for kv in url_parse.query.split("&")}
            xsec_token = kv_dist.get("xsec_token", "")
            xsec_source = kv_dist.get("xsec_source", "pc_user")
            while True:
                success, msg, res_json = self.get_user_like_note_info(user_id, cursor, cookies_str, xsec_token, xsec_source, proxies)
                if not success:
                    raise Exception(msg)
                notes = res_json["data"]["notes"]
                cursor = str(res_json["data"].get("cursor", ""))
                note_list.extend(notes)
                if len(notes) == 0 or not res_json["data"].get("has_more", False):
                    break
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, note_list

    def get_user_collect_note_info(
        self,
        user_id: str,
        cursor: str,
        cookies_str: str,
        xsec_token: str = "",
        xsec_source: str = "",
        proxies: Dict[str, str] | None = None,
    ) -> Tuple[bool, str, Any]:
        """Fetch collected notes at a cursor"""
        res_json = None
        try:
            api = "/api/sns/web/v2/note/collect/page"
            params = {
                "num": "30",
                "cursor": cursor,
                "user_id": user_id,
                "image_formats": "jpg,webp,avif",
                "xsec_token": xsec_token,
                "xsec_source": xsec_source,
            }
            splice_api = splice_str(api, params)
            headers, cookies, _ = generate_request_params(cookies_str, splice_api)
            response = self._get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def get_user_all_collect_note_info(self, user_url: str, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, List[Any]]:
        """Fetch all collected notes for a user"""
        cursor = ""
        note_list: List[Any] = []
        try:
            url_parse = urllib.parse.urlparse(user_url)
            user_id = url_parse.path.split("/")[-1]
            kv_dist = {kv.split("=")[0]: kv.split("=")[1] for kv in url_parse.query.split("&")}
            xsec_token = kv_dist.get("xsec_token", "")
            xsec_source = kv_dist.get("xsec_source", "pc_search")
            while True:
                success, msg, res_json = self.get_user_collect_note_info(user_id, cursor, cookies_str, xsec_token, xsec_source, proxies)
                if not success:
                    raise Exception(msg)
                notes = res_json["data"]["notes"]
                cursor = str(res_json["data"].get("cursor", ""))
                note_list.extend(notes)
                if len(notes) == 0 or not res_json["data"].get("has_more", False):
                    break
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, note_list

    def get_note_info(self, url: str, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, Any]:
        """Get note details"""
        res_json = None
        try:
            url_parse = urllib.parse.urlparse(url)
            note_id = url_parse.path.split("/")[-1]
            kv_dist = {kv.split("=")[0]: kv.split("=")[1] for kv in url_parse.query.split("&")}
            api = "/api/sns/web/v1/feed"
            data = {
                "source_note_id": note_id,
                "image_formats": ["jpg", "webp", "avif"],
                "extra": {"need_body_topic": "1"},
                "xsec_source": kv_dist.get("xsec_source", "pc_search"),
                "xsec_token": kv_dist["xsec_token"],
            }
            headers, cookies, data = generate_request_params(cookies_str, api, data)
            response = self._post(self.base_url + api, headers=headers, data=data, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    @staticmethod
    def get_note_no_water_video(note_id: str) -> Tuple[bool, str, Any]:
        """Get video URL without watermark"""
        success = True
        msg = "成功"
        video_addr = None
        try:
            headers = get_common_headers()
            url = f"https://www.xiaohongshu.com/explore/{note_id}"
            response = self._get(url, headers=headers)
            res = response.text
            video_addr = re.findall(r'<meta name="og:video" content="(.*?)">', res)[0]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, video_addr

    @staticmethod
    def get_note_no_water_img(img_url: str) -> Tuple[bool, str, Any]:
        """Get image URL without watermark"""
        success = True
        msg = "成功"
        new_url = None
        try:
            if ".jpg" in img_url:
                img_id = "/".join(img_url.split("/")[-3:]).split("!")[0]
                new_url = f"https://sns-img-qc.xhscdn.com/{img_id}"
            elif "spectrum" in img_url:
                img_id = "/".join(img_url.split("/")[-2:]).split("!")[0]
                new_url = f"http://sns-webpic.xhscdn.com/{img_id}?imageView2/2/w/format/jpg"
            else:
                img_id = img_url.split("/")[-1].split("!")[0]
                new_url = f"https://sns-img-qc.xhscdn.com/{img_id}"
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, new_url
