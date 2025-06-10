from __future__ import annotations
from typing import Tuple, List, Dict, Any
import urllib
from xhs_utils.xhs_util import splice_str, generate_request_params
from .base import BaseAPI


class CommentAPI(BaseAPI):
    def get_note_out_comment(
        self,
        note_id: str,
        cursor: str,
        xsec_token: str,
        cookies_str: str,
        proxies: Dict[str, str] | None = None,
    ) -> Tuple[bool, str, Any]:
        """Fetch first level comments"""
        res_json = None
        try:
            api = "/api/sns/web/v2/comment/page"
            params = {
                "note_id": note_id,
                "cursor": cursor,
                "top_comment_id": "",
                "image_formats": "jpg,webp,avif",
                "xsec_token": xsec_token,
            }
            splice_api = splice_str(api, params)
            headers, cookies, _ = generate_request_params(cookies_str, splice_api)
            response = self._get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def get_note_all_out_comment(
        self,
        note_id: str,
        xsec_token: str,
        cookies_str: str,
        proxies: Dict[str, str] | None = None,
    ) -> Tuple[bool, str, List[Any]]:
        """Fetch all first level comments"""
        cursor = ""
        comment_list: List[Any] = []
        try:
            while True:
                success, msg, res_json = self.get_note_out_comment(note_id, cursor, xsec_token, cookies_str, proxies)
                if not success:
                    raise Exception(msg)
                comments = res_json["data"]["comments"]
                cursor = str(res_json["data"].get("cursor", ""))
                comment_list.extend(comments)
                if len(comment_list) == 0 or not res_json["data"].get("has_more", False):
                    break
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, comment_list

    def get_note_inner_comment(
        self,
        comment: Dict[str, Any],
        cursor: str,
        xsec_token: str,
        cookies_str: str,
        proxies: Dict[str, str] | None = None,
    ) -> Tuple[bool, str, Any]:
        """Fetch second level comments"""
        res_json = None
        try:
            api = "/api/sns/web/v2/comment/sub/page"
            params = {
                "note_id": comment["note_id"],
                "root_comment_id": comment["id"],
                "num": "10",
                "cursor": cursor,
                "image_formats": "jpg,webp,avif",
                "top_comment_id": "",
                "xsec_token": xsec_token,
            }
            splice_api = splice_str(api, params)
            headers, cookies, _ = generate_request_params(cookies_str, splice_api)
            response = self._get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def get_note_all_inner_comment(
        self,
        comment: Dict[str, Any],
        xsec_token: str,
        cookies_str: str,
        proxies: Dict[str, str] | None = None,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Fetch all second level comments for a comment"""
        try:
            if not comment.get("sub_comment_has_more"):
                return True, "success", comment
            cursor = comment["sub_comment_cursor"]
            inner_comment_list: List[Any] = []
            while True:
                success, msg, res_json = self.get_note_inner_comment(comment, cursor, xsec_token, cookies_str, proxies)
                if not success:
                    raise Exception(msg)
                comments = res_json["data"]["comments"]
                cursor = str(res_json["data"].get("cursor", ""))
                inner_comment_list.extend(comments)
                if not res_json["data"].get("has_more", False):
                    break
            comment["sub_comments"].extend(inner_comment_list)
            success, msg = True, "success"
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, comment

    def get_note_all_comment(self, url: str, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, List[Any]]:
        """Fetch all comments for a note"""
        out_comment_list: List[Any] = []
        try:
            url_parse = urllib.parse.urlparse(url)
            note_id = url_parse.path.split("/")[-1]
            kv_dist = {kv.split("=")[0]: kv.split("=")[1] for kv in url_parse.query.split("&")}
            success, msg, out_comment_list = self.get_note_all_out_comment(note_id, kv_dist["xsec_token"], cookies_str, proxies)
            if not success:
                raise Exception(msg)
            for comment in out_comment_list:
                success, msg, new_comment = self.get_note_all_inner_comment(comment, kv_dist["xsec_token"], cookies_str, proxies)
                if not success:
                    raise Exception(msg)
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, out_comment_list

    def get_unread_message(self, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, Any]:
        """Fetch unread message count"""
        res_json = None
        try:
            api = "/api/sns/web/unread_count"
            headers, cookies, _ = generate_request_params(cookies_str, api)
            response = self._get(self.base_url + api, headers=headers, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def get_metions(self, cursor: str, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, Any]:
        """Fetch mentions"""
        res_json = None
        try:
            api = "/api/sns/web/v1/you/mentions"
            params = {"num": "20", "cursor": cursor}
            splice_api = splice_str(api, params)
            headers, cookies, _ = generate_request_params(cookies_str, splice_api)
            response = self._get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def get_all_metions(self, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, List[Any]]:
        """Fetch all mentions"""
        cursor = ""
        metion_list: List[Any] = []
        try:
            while True:
                success, msg, res_json = self.get_metions(cursor, cookies_str, proxies)
                if not success:
                    raise Exception(msg)
                metions = res_json["data"]["message_list"]
                cursor = str(res_json["data"].get("cursor", ""))
                metion_list.extend(metions)
                if not res_json["data"].get("has_more", False):
                    break
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, metion_list

    def get_likesAndcollects(self, cursor: str, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, Any]:
        """Fetch likes and collects"""
        res_json = None
        try:
            api = "/api/sns/web/v1/you/likes"
            params = {"num": "20", "cursor": cursor}
            splice_api = splice_str(api, params)
            headers, cookies, _ = generate_request_params(cookies_str, splice_api)
            response = self._get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def get_all_likesAndcollects(self, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, List[Any]]:
        """Fetch all likes and collects"""
        cursor = ""
        lc_list: List[Any] = []
        try:
            while True:
                success, msg, res_json = self.get_likesAndcollects(cursor, cookies_str, proxies)
                if not success:
                    raise Exception(msg)
                lcs = res_json["data"]["message_list"]
                cursor = str(res_json["data"].get("cursor", ""))
                lc_list.extend(lcs)
                if not res_json["data"].get("has_more", False):
                    break
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, lc_list

    def get_new_connections(self, cursor: str, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, Any]:
        """Fetch new connections"""
        res_json = None
        try:
            api = "/api/sns/web/v1/you/connections"
            params = {"num": "20", "cursor": cursor}
            splice_api = splice_str(api, params)
            headers, cookies, _ = generate_request_params(cookies_str, splice_api)
            response = self._get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            res_json = response.json()
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, res_json

    def get_all_new_connections(self, cookies_str: str, proxies: Dict[str, str] | None = None) -> Tuple[bool, str, List[Any]]:
        """Fetch all new connections"""
        cursor = ""
        connection_list: List[Any] = []
        try:
            while True:
                success, msg, res_json = self.get_new_connections(cursor, cookies_str, proxies)
                if not success:
                    raise Exception(msg)
                cons = res_json["data"]["message_list"]
                cursor = str(res_json["data"].get("cursor", ""))
                connection_list.extend(cons)
                if not res_json["data"].get("has_more", False):
                    break
        except Exception as e:
            success, msg = False, str(e)
        return success, msg, connection_list
