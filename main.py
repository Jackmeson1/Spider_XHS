import json
import os
import argparse
from loguru import logger
from apis.xhs_pc_apis import XHS_Apis
from xhs_utils.common_util import init
from xhs_utils.data_util import handle_note_info, download_note, save_to_xlsx


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

    def spider_some_note(self, notes: list, cookies_str: str, base_path: dict, save_choice: str, excel_name: str = '', proxies=None):
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
        for note_url in notes:
            success, msg, note_info = self.spider_note(note_url, cookies_str, proxies)
            if note_info is not None and success:
                note_list.append(note_info)
        for note_info in note_list:
            if save_choice == 'all' or 'media' in save_choice:
                download_note(note_info, base_path['media'], save_choice)
        if save_choice == 'all' or save_choice == 'excel':
            file_path = os.path.abspath(os.path.join(base_path['excel'], f'{excel_name}.xlsx'))
            save_to_xlsx(note_list, file_path)


    def spider_user_all_note(self, user_url: str, cookies_str: str, base_path: dict, save_choice: str, excel_name: str = '', proxies=None):
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
                for simple_note_info in all_note_info:
                    note_url = f"https://www.xiaohongshu.com/explore/{simple_note_info['note_id']}?xsec_token={simple_note_info['xsec_token']}"
                    note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                excel_name = user_url.split('/')[-1].split('?')[0]
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'爬取用户所有视频 {user_url}: {success}, msg: {msg}')
        return note_list, success, msg

    def spider_some_search_note(self, query: str, require_num: int, cookies_str: str, base_path: dict, save_choice: str, sort_type_choice=0, note_type=0, note_time=0, note_range=0, pos_distance=0, geo: dict = None,  excel_name: str = '', proxies=None):
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
            success, msg, notes = self.xhs_apis.search_some_note(query, require_num, cookies_str, sort_type_choice, note_type, note_time, note_range, pos_distance, geo, proxies)
            if success:
                notes = list(filter(lambda x: x['model_type'] == "note", notes))
                logger.info(f'搜索关键词 {query} 笔记数量: {len(notes)}')
                for note in notes:
                    note_url = f"https://www.xiaohongshu.com/explore/{note['id']}?xsec_token={note['xsec_token']}"
                    note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                excel_name = query
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'搜索关键词 {query} 笔记: {success}, msg: {msg}')
        return note_list, success, msg


def example_usage():
    """Run the original example code."""
    cookies_str, base_path = init()
    data_spider = Data_Spider()

    # 1 爬取列表的所有笔记信息
    notes = [
        r'https://www.xiaohongshu.com/explore/683fe17f0000000023017c6a?xsec_token=ABBr_cMzallQeLyKSRdPk9fwzA0torkbT_ubuQP1ayvKA=&xsec_source=pc_user',
    ]
    data_spider.spider_some_note(notes, cookies_str, base_path, 'all', 'test')

    # 2 爬取用户的所有笔记信息
    user_url = 'https://www.xiaohongshu.com/user/profile/64c3f392000000002b009e45?xsec_token=AB-GhAToFu07JwNk_AMICHnp7bSTjVz2beVIDBwSyPwvM=&xsec_source=pc_feed'
    data_spider.spider_user_all_note(user_url, cookies_str, base_path, 'all')

    # 3 搜索指定关键词的笔记
    query = "榴莲"
    query_num = 10
    sort_type_choice = 0
    note_type = 0
    note_time = 0
    note_range = 0
    pos_distance = 0
    data_spider.spider_some_search_note(query, query_num, cookies_str, base_path, 'all', sort_type_choice, note_type, note_time, note_range, pos_distance, geo=None)


def parse_args():
    parser = argparse.ArgumentParser(description='Spider XHS command line interface')
    subparsers = parser.add_subparsers(dest='command')

    note_parser = subparsers.add_parser('note', help='Crawl specified notes')
    note_parser.add_argument('--urls', nargs='+', required=True, help='note urls')
    note_parser.add_argument('--save-choice', default='all', help='save option')
    note_parser.add_argument('--excel-name', default='notes', help='excel filename')

    user_parser = subparsers.add_parser('user', help='Crawl all notes of a user')
    user_parser.add_argument('--url', required=True, help='user url')
    user_parser.add_argument('--save-choice', default='all', help='save option')
    user_parser.add_argument('--excel-name', default='', help='excel filename')

    search_parser = subparsers.add_parser('search', help='Search notes by keyword')
    search_parser.add_argument('--keyword', required=True, help='search keyword')
    search_parser.add_argument('--count', type=int, default=10, help='number of notes')
    search_parser.add_argument('--save-choice', default='all', help='save option')
    search_parser.add_argument('--excel-name', default='', help='excel filename')
    search_parser.add_argument('--sort-type', type=int, default=0, help='sort type')
    search_parser.add_argument('--note-type', type=int, default=0, help='note type')
    search_parser.add_argument('--note-time', type=int, default=0, help='note time')
    search_parser.add_argument('--note-range', type=int, default=0, help='note range')
    search_parser.add_argument('--pos-distance', type=int, default=0, help='position distance')
    search_parser.add_argument('--latitude', type=float, help='geo latitude')
    search_parser.add_argument('--longitude', type=float, help='geo longitude')

    parser.add_argument('--example', action='store_true', help='run example usage')
    return parser.parse_args()


def main():
    args = parse_args()

    if args.example and args.command is None:
        example_usage()
        return

    cookies_str, base_path = init()
    spider = Data_Spider()

    if args.command == 'note':
        spider.spider_some_note(args.urls, cookies_str, base_path, args.save_choice, args.excel_name)
    elif args.command == 'user':
        spider.spider_user_all_note(args.url, cookies_str, base_path, args.save_choice, args.excel_name)
    elif args.command == 'search':
        geo = None
        if args.latitude is not None and args.longitude is not None:
            geo = {'latitude': args.latitude, 'longitude': args.longitude}
        spider.spider_some_search_note(
            args.keyword,
            args.count,
            cookies_str,
            base_path,
            args.save_choice,
            args.sort_type,
            args.note_type,
            args.note_time,
            args.note_range,
            args.pos_distance,
            geo,
            args.excel_name,
        )
    else:
        example_usage()


if __name__ == '__main__':
    main()
