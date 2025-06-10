import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from typer.testing import CliRunner
from cli import app
from main import Data_Spider

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert "Usage" in result.stdout

def test_cli_crawl(monkeypatch, tmp_path):
    def fake_spider(self, notes, cookie, base, save_choice, excel_name, proxies=None, transcode=False):
        fake_spider.args = (notes, cookie, base, save_choice, excel_name, transcode)
    monkeypatch.setattr(Data_Spider, "spider_some_note", fake_spider)
    out_dir = tmp_path / "out"
    result = runner.invoke(
        app,
        [
            "crawl",
            "--cookie",
            "c",
            "--note-id",
            "n1",
            "--save-choice",
            "excel",
            "--excel-name",
            "out",
            "--output-dir",
            str(out_dir),
        ],
    )
    assert result.exit_code == 0
    assert fake_spider.args[0] == ["https://www.xiaohongshu.com/explore/n1"]
    assert fake_spider.args[1] == "c"
    assert fake_spider.args[3] == "excel"
    assert fake_spider.args[4] == "out"
    assert out_dir.joinpath("media").exists()
    assert out_dir.joinpath("excel").exists()


def test_cli_validation(monkeypatch):
    result = runner.invoke(app, ["crawl", "--cookie", "", "--note-id", ""])
    assert result.exit_code != 0
    assert "note-id is invalid" in result.stderr or "cookie cannot be empty" in result.stderr

    result = runner.invoke(app, ["crawl", "--cookie", "c", "--note-id", "n1", "--save-choice", "excel"])
    assert result.exit_code != 0
    assert "--excel-name is required" in result.stderr
