import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from typer.testing import CliRunner
from cli import app
from main import Data_Spider

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["crawl", "--help"])
    assert "--note-url" in result.stdout

def test_cli_crawl_with_id(monkeypatch):
    def fake_spider(self, url, cookie, proxies=None):
        return True, "ok", {"id": "n1"}
    monkeypatch.setattr(Data_Spider, "spider_note", fake_spider)
    result = runner.invoke(app, ["crawl", "--cookie", "c", "--note-id", "n1"])
    assert "Crawled n1 successfully" in result.stdout


def test_cli_crawl_with_url(monkeypatch):
    def fake_spider(self, url, cookie, proxies=None):
        assert url == "http://x.com/n1"
        return True, "ok", {"id": "n1"}

    monkeypatch.setattr(Data_Spider, "spider_note", fake_spider)
    result = runner.invoke(app, ["crawl", "--cookie", "c", "--note-url", "http://x.com/n1"])
    assert "Crawled http://x.com/n1 successfully" in result.stdout


def test_cli_validation(monkeypatch):
    # empty cookie and missing identifiers
    result = runner.invoke(app, ["crawl", "--cookie", "", "--note-id", ""])
    assert result.exit_code != 0
    assert "note-id is invalid" in result.stderr or "cookie cannot be empty" in result.stderr

    # valid cookie but no id or url
    result = runner.invoke(app, ["crawl", "--cookie", "c", "--note-id", ""]) 
    assert result.exit_code != 0
    assert "note-id is invalid" in result.stderr
