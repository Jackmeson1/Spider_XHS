import sys
import pathlib
from pathlib import Path

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from typer.testing import CliRunner
from cli import app
from main import Data_Spider

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert "Usage" in result.stdout

def test_cli_crawl(monkeypatch, tmp_path):
    params = {}
    def fake_spider(self, notes, cookie, base_path, save_choice, excel_name, proxies=None, transcode=False):
        params['notes'] = notes
        params['cookie'] = cookie
        params['base'] = base_path
        return None
    monkeypatch.setattr(Data_Spider, "spider_some_note", fake_spider)
    note_id = "a" * 24
    out = tmp_path / "out"
    result = runner.invoke(app, [
        "crawl",
        "--cookie",
        "c",
        "--note-id",
        note_id,
        "--output-dir",
        str(out),
        "--save-choice",
        "excel",
        "--excel-name",
        "data",
    ])
    assert result.exit_code == 0
    assert params['notes'][0].endswith(note_id)
    assert params['cookie'] == "c"
    assert Path(params['base']['media']).exists()


def test_cli_validation(monkeypatch):
    result = runner.invoke(app, ["crawl", "--cookie", "", "--note-id", ""])
    assert result.exit_code != 0
    assert "note-id is invalid" in result.stderr or "cookie cannot be empty" in result.stderr


def test_cli_env_cookie(monkeypatch):
    params = {}
    def fake_spider(self, notes, cookie, base_path, save_choice, excel_name, proxies=None, transcode=False):
        params['cookie'] = cookie
    monkeypatch.setattr(Data_Spider, "spider_some_note", fake_spider)
    monkeypatch.setenv("COOKIES", "envc")
    note_id = "a" * 24
    result = runner.invoke(app, ["crawl", "--note-id", note_id])
    assert result.exit_code == 0
    assert params['cookie'] == "envc"


def test_invalid_note_id_short(monkeypatch):
    result = runner.invoke(app, ["crawl", "--cookie", "c", "--note-id", "abc"])
    assert result.exit_code != 0
    assert "note-id is invalid" in result.stderr


def test_invalid_note_id_path(monkeypatch):
    result = runner.invoke(app, ["crawl", "--cookie", "c", "--note-id", "../../etc/passwd"])
    assert result.exit_code != 0
    assert "note-id is invalid" in result.stderr


def test_note_url_overrides_id(monkeypatch):
    params = {}
    def fake_spider(self, notes, cookie, base_path, save_choice, excel_name, proxies=None, transcode=False):
        params['notes'] = notes
    monkeypatch.setattr(Data_Spider, "spider_some_note", fake_spider)
    result = runner.invoke(app, ["crawl", "--cookie", "c", "--note-url", "http://x.com/n1"])
    assert result.exit_code == 0
    assert params['notes'] == ["http://x.com/n1"]

