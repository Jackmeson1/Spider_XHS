import json
import os
import argparse
import time
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
from xhs_utils.retry_util import retry_with_backoff, smart_delay
from xhs_utils.error_handler import XHSAuthError, XHSRateLimitError, XHSNotFoundError
from tqdm import tqdm


class Data_Spider():
    def __init__(self):
        self.xhs_apis = XHS_Apis()
        self.last_request_time = 0

    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def spider_note(self, note_url: str, cookies_str: str, proxies=None):
        """Crawl information for a single note."""
        note_info = None
        try:
            # Add intelligent delay between requests
            smart_delay(self.last_request_time, min_interval=2.0)
            self.last_request_time = time.time()
            
            success, msg, response_data = self.xhs_apis.get_note_info(note_url, cookies_str, proxies)
            if success and response_data:
                if 'data' not in response_data or 'items' not in response_data['data']:
                    raise ValueError(f"Invalid response structure: {response_data}")
                
                items = response_data['data']['items']
                if not items:
                    raise ValueError("No items found in response")
                    
                note_info = items[0]
                note_info['url'] = note_url
                note_info = handle_note_info(note_info)
            else:
                raise Exception(msg)
                
        except (XHSAuthError, XHSRateLimitError, XHSNotFoundError) as e:
            success = False
            msg = str(e)
            logger.error(f'XHS error crawling note {note_url}: {e}')
        except Exception as e:
            success = False
            msg = str(e)
            logger.error(f'Unexpected error crawling note {note_url}: {e}')
            
        logger.info(f'Crawled note info {note_url}: {success}, msg: {msg}')
        return success, msg, note_info

    def spider_some_note(
        self,
        notes: list,
        cookies_str: str,
        base_path: dict,
        save_choice: str,
        excel_name: str = '',
        proxies=None,
        transcode: bool = False,
    ):
        """Crawl a batch of notes."""
        if (save_choice == 'all' or save_choice == 'excel') and excel_name == '':
            raise ValueError('excel_name cannot be empty')
        note_list = []
        for note_url in tqdm(notes, desc="notes"):
            success, msg, note_info = self.spider_note(note_url, cookies_str, proxies)
            if note_info is not None and success:
                note_list.append(note_info)
        failed = []
        for note_info in tqdm(note_list, desc="download"):
            if save_choice == 'all' or 'media' in save_choice or 'flat' in save_choice:
                download_note(note_info, base_path['media'], save_choice, transcode, failed)
        if save_choice == 'all' or save_choice == 'excel':
            file_path = os.path.abspath(os.path.join(base_path['excel'], f'{excel_name}.xlsx'))
            save_to_xlsx(note_list, file_path)
        save_failed(failed)


    def spider_user_all_note(
        self,
        user_url: str,
        cookies_str: str,
        base_path: dict,
        save_choice: str,
        excel_name: str = '',
        proxies=None,
        transcode: bool = False,
    ):
        """Crawl all notes posted by a user."""
        note_list = []
        try:
            success, msg, all_note_info = self.xhs_apis.get_user_all_notes(user_url, cookies_str, proxies)
            if success:
                logger.info(f'User {user_url} has {len(all_note_info)} notes')
                for simple_note_info in tqdm(all_note_info, desc="notes"):
                    note_url = f"https://www.xiaohongshu.com/explore/{simple_note_info['note_id']}?xsec_token={simple_note_info['xsec_token']}"
                    note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                excel_name = user_url.split('/')[-1].split('?')[0]
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies, transcode)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'Crawled all notes for {user_url}: {success}, msg: {msg}')
        return note_list, success, msg

    def spider_some_search_note(
        self,
        query: str,
        require_num: int,
        cookies_str: str,
        base_path: dict,
        save_choice: str,
        sort_type_choice=0,
        note_type=0,
        note_time=0,
        note_range=0,
        pos_distance=0,
        geo: dict | None = None,
        excel_name: str = '',
        proxies=None,
        transcode: bool = False,
    ):
        """Search and crawl a fixed number of notes.

        :param query: keyword to search
        :param require_num: number of notes to fetch
        :param cookies_str: authentication cookies
        :param base_path: output directories
        :param sort_type_choice: 0 general, 1 newest, 2 most liked, 3 most commented, 4 most collected
        :param note_type: 0 all, 1 video note, 2 normal note
        :param note_time: 0 all, 1 within a day, 2 within a week, 3 within half a year
        :param note_range: 0 all, 1 viewed, 2 not viewed, 3 followed
        :param pos_distance: 0 all, 1 same city, 2 nearby (requires geo)
        :return: list of note urls
        """
        note_list = []
        try:
            success, msg, notes = self.xhs_apis.search_some_note(query, require_num, cookies_str, sort_type_choice, note_type, note_time, note_range, pos_distance, geo, proxies)
            if success:
                notes = list(filter(lambda x: x['model_type'] == "note", notes))
                logger.info(f'Search "{query}" found {len(notes)} notes')
                for note in tqdm(notes, desc="notes"):
                    note_url = f"https://www.xiaohongshu.com/explore/{note['id']}?xsec_token={note['xsec_token']}"
                    note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                excel_name = query
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies, transcode)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'Search "{query}" result: {success}, msg: {msg}')
        return note_list, success, msg

def run_examples():
    """Demonstrate typical usage of the spider."""
    cookies_str, base_path = init()
    data_spider = Data_Spider()
    """
    Example options for ``save_choice``:
    - ``all``: save Excel and all media
    - ``media``: save both videos and images (``media-video`` only videos,
      ``media-image`` only images)
    - ``image-flat``: store images directly in the media folder as
      ``<note_id>_<index>.jpg``
    - ``video-flat``: store video directly in the media folder as
      ``<note_id>.mp4``
    - ``excel``: only save to Excel
    ``excel_name`` must be provided when using ``excel`` or ``all``
    """


    # 1 Crawl the notes from the list below (URLs expire quickly)
    notes = [
        r'https://www.xiaohongshu.com/explore/683fe17f0000000023017c6a?xsec_token=ABBr_cMzallQeLyKSRdPk9fwzA0torkbT_ubuQP1ayvKA=&xsec_source=pc_user',
    ]
    data_spider.spider_some_note(notes, cookies_str, base_path, 'all', 'test')

    # 2 Crawl all notes from a user (URL may expire)
    user_url = 'https://www.xiaohongshu.com/user/profile/64c3f392000000002b009e45?xsec_token=AB-GhAToFu07JwNk_AMICHnp7bSTjVz2beVIDBwSyPwvM=&xsec_source=pc_feed'
    data_spider.spider_user_all_note(user_url, cookies_str, base_path, 'all')

    # 3 Search notes by keyword
    query = "durian"
    query_num = 10
    sort_type_choice = 0  # 0 general, 1 newest, 2 most liked, 3 most commented, 4 most collected
    note_type = 0  # 0 all, 1 video note, 2 normal note
    note_time = 0  # 0 all, 1 within a day, 2 within a week, 3 within half a year
    note_range = 0  # 0 all, 1 viewed, 2 not viewed, 3 followed
    pos_distance = 0  # 0 all, 1 same city, 2 nearby (geo required when 1 or 2)
    # geo = {
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

    cookies_str, base_path = init()
    spider = Data_Spider()

    if args.retry_failed:
        records = retry_failed("failed.txt")
        for item in tqdm(records, desc="retry"):
            download_media(item["path"], item["name"], item["url"], item["type"])
        return

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


if __name__ == '__main__':
    cli()
