import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import pytest
from main import Data_Spider, cli
from xhs_utils.data_util import save_to_xlsx


def sample_note():
    return {
        'note_id': 'n1',
        'note_url': 'http://x.com/n1',
        'note_type': '图集',
        'user_id': 'u1',
        'home_url': 'http://x.com/u1',
        'nickname': 'nick',
        'avatar': 'a.jpg',
        'title': 'title',
        'desc': 'desc',
        'liked_count': 1,
        'collected_count': 2,
        'comment_count': 3,
        'share_count': 4,
        'video_cover': None,
        'video_addr': None,
        'image_list': [],
        'tags': [],
        'upload_time': 't',
        'ip_location': 'loc',
    }


def test_no_excel_file_on_failure(tmp_path, monkeypatch):
    spider = Data_Spider()

    def fake_note(url, cookies, proxies=None):
        return False, "err", None

    monkeypatch.setattr(spider, "spider_note", fake_note)
    base = {'media': str(tmp_path / 'media'), 'excel': str(tmp_path / 'excel')}
    spider.spider_some_note(['badurl'], 'c', base, 'excel', excel_name='out')
    assert not (tmp_path / 'excel' / 'out.xlsx').exists()


def test_missing_excel_name_validation(monkeypatch, capsys):
    argv = ['main.py', '--notes', 'http://x.com/n1', '--save-choice', 'excel']
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        cli()
    out = capsys.readouterr().err
    assert '--excel-name is required' in out


def test_invalid_url_message():
    spider = Data_Spider()
    success, msg, info = spider.spider_note('invalid_url', 'c')
    assert not success
    assert msg == 'Invalid note URL'
    assert info is None


def test_save_to_xlsx_creates_dir(tmp_path):
    file_path = tmp_path / 'newdir' / 'file.xlsx'
    save_to_xlsx([sample_note()], str(file_path))
    assert file_path.exists()
