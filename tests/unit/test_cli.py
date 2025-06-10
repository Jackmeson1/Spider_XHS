import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from typer.testing import CliRunner
from cli import app
from main import Data_Spider

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert "Usage" in result.stdout

def test_cli_crawl(monkeypatch):
    def fake_spider(self, url, cookie, proxies=None):
        return True, "ok", {"id": "n1"}
    monkeypatch.setattr(Data_Spider, "spider_note", fake_spider)
    note_id = "a" * 24
    result = runner.invoke(app, ["crawl", "--cookie", "c", "--note-id", note_id])
    assert f"Crawled {note_id} successfully" in result.stdout


def test_cli_validation(monkeypatch):
    result = runner.invoke(app, ["crawl", "--cookie", "", "--note-id", ""])
    assert result.exit_code != 0
    assert "note-id is invalid" in result.stderr or "cookie cannot be empty" in result.stderr


def test_invalid_note_id_short(monkeypatch):
    result = runner.invoke(app, ["crawl", "--cookie", "c", "--note-id", "abc"])
    assert result.exit_code != 0
    assert "note-id is invalid" in result.stderr


def test_invalid_note_id_path(monkeypatch):
    result = runner.invoke(app, ["crawl", "--cookie", "c", "--note-id", "../../etc/passwd"])
    assert result.exit_code != 0
    assert "note-id is invalid" in result.stderr
