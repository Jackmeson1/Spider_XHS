import json
import os
import re
import argparse
from loguru import logger
from apis.xhs_pc_apis import XHS_Apis
from xhs_utils.common_util import init
from xhs_utils.data_util import (
    handle_note_info,
    download_note,
    save_to_xlsx,
    save_failed,
    retry_failed,
    download_media,
)
from tqdm import tqdm


class Data_Spider():
    def __init__(self):
        self.xhs_apis = XHS_Apis()

    def spider_note(self, note_url: str, cookies_str: str, proxies=None):
        """
        爬取一个笔记的信息
        :param note_url:
        :param cookies_str:
        :return:
        """
        note_info = None
        # basic url validation to provide helpful error messages
        if not re.match(r"https?://", note_url):
            msg = "Invalid note URL"
            logger.error(f"{msg}: {note_url}")
            return False, msg, None
        try:
            success, msg, note_info = self.xhs_apis.get_note_info(note_url, cookies_str, proxies)
            if success:
                note_info = note_info['data']['items'][0]
                note_info['url'] = note_url
                note_info = handle_note_info(note_info)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'爬取笔记信息 {note_url}: {success}, msg: {msg}')
        return success, msg, note_info

    def spider_some_note(self, notes: list, cookies_str: str, base_path: dict, save_choice: str, excel_name: str = '', proxies=None, transcode: bool = False):
        """
        爬取一些笔记的信息
        :param notes:
        :param cookies_str:
        :param base_path:
        :return:
        """
        if (save_choice == 'all' or save_choice == 'excel') and excel_name == '':
            raise ValueError('excel_name 不能为空')
        note_list = []
        for note_url in tqdm(notes, desc="notes"):
            success, msg, note_info = self.spider_note(note_url, cookies_str, proxies)
            if note_info is not None and success:
                note_list.append(note_info)
        failed = []
        for note_info in tqdm(note_list, desc="download"):
            if save_choice == 'all' or 'media' in save_choice or 'flat' in save_choice:
                download_note(note_info, base_path['media'], save_choice, transcode, failed)
        if (save_choice == 'all' or save_choice == 'excel') and note_list:
            file_path = os.path.abspath(os.path.join(base_path['excel'], f'{excel_name}.xlsx'))
            save_to_xlsx(note_list, file_path)
        elif save_choice in ('all', 'excel') and not note_list:
            logger.error('No valid notes fetched; Excel file will not be created')
        save_failed(failed)


    def spider_user_all_note(self, user_url: str, cookies_str: str, base_path: dict, save_choice: str, excel_name: str = '', proxies=None, transcode: bool = False):
        """
        爬取一个用户的所有笔记
        :param user_url:
        :param cookies_str:
        :param base_path:
        :return:
        """
        note_list = []
        try:
            success, msg, all_note_info = self.xhs_apis.get_user_all_notes(user_url, cookies_str, proxies)
            if success:
                logger.info(f'用户 {user_url} 作品数量: {len(all_note_info)}')
                for simple_note_info in tqdm(all_note_info, desc="notes"):
                    note_url = f"https://www.xiaohongshu.com/explore/{simple_note_info['note_id']}?xsec_token={simple_note_info['xsec_token']}"
                    note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                excel_name = user_url.split('/')[-1].split('?')[0]
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies, transcode)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'爬取用户所有视频 {user_url}: {success}, msg: {msg}')
        return note_list, success, msg

    def spider_some_search_note(self, query: str, require_num: int, cookies_str: str, base_path: dict, save_choice: str, sort_type_choice=0, note_type=0, note_time=0, note_range=0, pos_distance=0, geo: dict = None,  excel_name: str = '', proxies=None, transcode: bool = False):
        """
            指定数量搜索笔记，设置排序方式和笔记类型和笔记数量
            :param query 搜索的关键词
            :param require_num 搜索的数量
            :param cookies_str 你的cookies
            :param base_path 保存路径
            :param sort_type_choice 排序方式 0 综合排序, 1 最新, 2 最多点赞, 3 最多评论, 4 最多收藏
            :param note_type 笔记类型 0 不限, 1 视频笔记, 2 普通笔记
            :param note_time 笔记时间 0 不限, 1 一天内, 2 一周内天, 3 半年内
            :param note_range 笔记范围 0 不限, 1 已看过, 2 未看过, 3 已关注
            :param pos_distance 位置距离 0 不限, 1 同城, 2 附近 指定这个必须要指定 geo
            返回搜索的结果
        """
        note_list = []
        try:
            success, msg, notes = self.xhs_apis.search_some_note(
                query,
                require_num,
                cookies_str,
                sort_type_choice,
                note_type,
                note_time,
                note_range,
                pos_distance,
                geo,
                proxies,
            )
            if success:
                notes = list(filter(lambda x: x['model_type'] == "note", notes))
                if not notes:
                    success = False
                    msg = f'No results for "{query}"'
                else:
                    logger.info(f'搜索关键词 {query} 笔记数量: {len(notes)}')
                    for note in tqdm(notes, desc="notes"):
                        note_url = f"https://www.xiaohongshu.com/explore/{note['id']}?xsec_token={note['xsec_token']}"
                        note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                excel_name = query
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies, transcode)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'搜索关键词 {query} 笔记: {success}, msg: {msg}')
        return note_list, success, msg

def run_examples():
    """Demonstrate typical usage of the spider."""
    cookies_str, base_path = init()
    data_spider = Data_Spider()
    """
        save_choice 说明:
        - all: 保存所有的信息
        - media: 保存视频和图片（media-video只下载视频, media-image只下载图片，media都下载）
        - image-flat: 图集直接保存在media路径下，文件名为<note_id>_<index>.jpg
        - video-flat: 视频直接保存在media路径下，文件名为<note_id>.mp4
        - excel: 仅保存到excel
        save_choice 为 excel 或者 all 时，excel_name 不能为空
    """


    # 1 爬取列表的所有笔记信息 笔记链接 如下所示 注意此url会过期！
    notes = [
        r'https://www.xiaohongshu.com/explore/683fe17f0000000023017c6a?xsec_token=ABBr_cMzallQeLyKSRdPk9fwzA0torkbT_ubuQP1ayvKA=&xsec_source=pc_user',
    ]
    data_spider.spider_some_note(notes, cookies_str, base_path, 'all', 'test')

    # 2 爬取用户的所有笔记信息 用户链接 如下所示 注意此url会过期！
    user_url = 'https://www.xiaohongshu.com/user/profile/64c3f392000000002b009e45?xsec_token=AB-GhAToFu07JwNk_AMICHnp7bSTjVz2beVIDBwSyPwvM=&xsec_source=pc_feed'
    data_spider.spider_user_all_note(user_url, cookies_str, base_path, 'all')

    # 3 搜索指定关键词的笔记
    query = "榴莲"
    query_num = 10
    sort_type_choice = 0  # 0 综合排序, 1 最新, 2 最多点赞, 3 最多评论, 4 最多收藏
    note_type = 0 # 0 不限, 1 视频笔记, 2 普通笔记
    note_time = 0  # 0 不限, 1 一天内, 2 一周内天, 3 半年内
    note_range = 0  # 0 不限, 1 已看过, 2 未看过, 3 已关注
    pos_distance = 0  # 0 不限, 1 同城, 2 附近 指定这个1或2必须要指定 geo
    # geo = {
    #     # 经纬度
    #     "latitude": 39.9725,
    #     "longitude": 116.4207
    # }
    data_spider.spider_some_search_note(query, query_num, cookies_str, base_path, 'all', sort_type_choice, note_type, note_time, note_range, pos_distance, geo=None)


def cli():
    parser = argparse.ArgumentParser(description="Spider XHS")
    parser.add_argument("--notes", nargs="*", help="note urls")
    parser.add_argument("--user", help="user url")
    parser.add_argument("--query", help="search keyword")
    parser.add_argument("--num", type=int, default=10, help="search count")
    parser.add_argument("--save-choice", default="all", help="save choice")
    parser.add_argument("--excel-name", default="", help="excel file name")
    parser.add_argument("--sort", type=int, default=0, help="sort type")
    parser.add_argument("--note-type", type=int, default=0)
    parser.add_argument("--note-time", type=int, default=0)
    parser.add_argument("--note-range", type=int, default=0)
    parser.add_argument("--pos-distance", type=int, default=0)
    parser.add_argument("--transcode", action="store_true")
    parser.add_argument("--retry-failed", action="store_true", help="retry failed downloads")
    args = parser.parse_args()

    if args.save_choice in ("excel", "all") and not args.excel_name:
        parser.exit(status=2, message="--excel-name is required when --save-choice is excel or all\n")

    cookies_str, base_path = init()
    spider = Data_Spider()

    if args.retry_failed:
        records = retry_failed("failed.txt")
        for item in tqdm(records, desc="retry"):
            download_media(item["path"], item["name"], item["url"], item["type"])
        return

    try:
        if args.notes:
            spider.spider_some_note(args.notes, cookies_str, base_path, args.save_choice, args.excel_name, transcode=args.transcode)
        if args.user:
            spider.spider_user_all_note(args.user, cookies_str, base_path, args.save_choice, args.excel_name, transcode=args.transcode)
        if args.query:
            spider.spider_some_search_note(
                args.query,
                args.num,
                cookies_str,
                base_path,
                args.save_choice,
                args.sort,
                args.note_type,
                args.note_time,
                args.note_range,
                args.pos_distance,
                geo=None,
                excel_name=args.excel_name,
                proxies=None,
                transcode=args.transcode,
            )
    except ValueError as e:
        parser.exit(status=2, message=f"{e}\n")
    except FileNotFoundError as e:
        parser.exit(status=2, message=f"{e}\n")


if __name__ == '__main__':
    cli()
