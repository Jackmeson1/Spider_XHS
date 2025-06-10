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
    result = runner.invoke(app, ["crawl", "--cookie", "c", "--note-id", "n1"])
    assert "Crawled n1 successfully" in result.stdout


def test_cli_env_cookie(monkeypatch):
    monkeypatch.setenv("COOKIES", "envc")

    def fake_spider(self, url, cookie, proxies=None):
        assert cookie == "envc"
        return True, "ok", {"id": "n1"}

    monkeypatch.setattr(Data_Spider, "spider_note", fake_spider)
    result = runner.invoke(app, ["crawl", "--note-id", "n1"])
    assert "Crawled n1 successfully" in result.stdout


def test_cli_validation(monkeypatch):
    result = runner.invoke(app, ["crawl", "--cookie", "", "--note-id", ""])
    assert result.exit_code != 0
    assert "note-id is invalid" in result.stderr or "cookie cannot be empty" in result.stderr
