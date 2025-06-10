import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import requests_mock
import os
import time
import pytest

from xhs_utils.data_util import (
    norm_str,
    timestamp_to_str,
    check_and_create_path,
    save_failed,
    retry_failed,
    download_media,
)
from freezegun import freeze_time
from xhs_utils.cookie_util import trans_cookies
from xhs_utils.xhs_util import generate_x_b3_traceid, splice_str


def test_norm_str():
    text = "inva/\\lid:*?<>|\n name"
    cleaned = norm_str(text)
    assert '/' not in cleaned and '*' not in cleaned and '\n' not in cleaned


@freeze_time("2021-01-01")
def test_timestamp_to_str():
    ts = 1609459200000  # 2021-01-01 00:00:00
    assert timestamp_to_str(ts) == "2021-01-01 00:00:00"


def test_trans_cookies():
    cookies = trans_cookies("a=1; b=2")
    assert cookies == {"a": "1", "b": "2"}
    cookies = trans_cookies("a=1;b=2")
    assert cookies == {"a": "1", "b": "2"}


def test_generate_x_b3_traceid():
    trace = generate_x_b3_traceid(16)
    assert len(trace) == 16
    int(trace, 16)


def test_splice_str():
    url = splice_str("/api", {"a": "1", "b": "2"})
    assert url == "/api?a=1&b=2"


def test_check_and_create_path(tmp_path):
    target = tmp_path / "newdir"
    check_and_create_path(target)
    assert target.exists()


def test_save_and_retry_failed(tmp_path):
    file_path = tmp_path / "failed.txt"
    save_failed([{"path": "p", "name": "n", "url": "u", "type": "image"}], file_path)
    records = retry_failed(file_path)
    assert records[0]["name"] == "n"


def test_download_media_image(tmp_path):
    url = "http://example.com/img.jpg"
    with requests_mock.Mocker() as m:
        m.get(url, content=b"data")
        result = download_media(str(tmp_path), "img", url, "image")
    assert result
    assert (tmp_path / "img.jpg").exists()


def test_download_media_video(tmp_path):
    url = "http://example.com/video.mp4"
    content = b"\x00\x00\x00\x18ftypmp42"  # minimal mp4 header
    with requests_mock.Mocker() as m:
        m.get(url, content=content)
        result = download_media(str(tmp_path), "vid", url, "video")
    assert result
    assert (tmp_path / "vid.mp4").exists()


def test_timestamp_negative():
    with pytest.raises(ValueError):
        timestamp_to_str(-1000)


def test_timestamp_timezone_independent(monkeypatch):
    monkeypatch.setenv("TZ", "Asia/Shanghai")
    if hasattr(time, "tzset"):
        time.tzset()
    ts = 1609459200000  # 2021-01-01 00:00:00 UTC
    assert timestamp_to_str(ts) == "2021-01-01 00:00:00"

