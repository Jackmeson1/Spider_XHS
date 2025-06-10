import os
import re
from pathlib import Path
from typing import Optional

import typer
from main import Data_Spider
from xhs_utils.common_util import init


def validate_note_id(value: str) -> str:
    """Validate note ID format."""
    pattern = r"^[0-9a-f]{24}$"
    if not value or not re.fullmatch(pattern, value.strip()):
        raise typer.BadParameter("note-id is invalid")
    return value

app = typer.Typer(help="XHS Spider command line interface")

@app.command()
def version() -> None:
    """Show tool version."""
    typer.echo("xhs-spider 0.1")

@app.command()
def crawl(
    cookie: Optional[str] = typer.Option(
        None, help="Xiaohongshu cookie"
    ),
    note_id: Optional[str] = typer.Option(
        None, help="Note ID to crawl"
    ),
    note_url: Optional[str] = typer.Option(
        None, help="Full note URL (recommended)"
    ),
    output_dir: Optional[str] = typer.Option(
        None, help="Directory to save outputs"
    ),
    excel_name: str = typer.Option(
        "", help="Excel file name when saving data"
    ),
    save_choice: str = typer.Option(
        "all",
        help="Save choice: all, excel, media, media-image, media-video, image-flat, video-flat",
    ),
    transcode: bool = typer.Option(
        False, help="Transcode videos to H264"
    ),
    rate_limit: float = typer.Option(
        0.0, help="Delay between requests in seconds"
    ),
):
    """Crawl a single note."""
    if cookie is None:
        cookie = os.getenv("COOKIES")
    if not cookie or not cookie.strip():
        raise typer.BadParameter("cookie cannot be empty")

    if note_url:
        url = note_url
    else:
        if note_id is None:
            raise typer.BadParameter("either --note-url or --note-id is required")
        validate_note_id(note_id)
        url = f"https://www.xiaohongshu.com/explore/{note_id}"

    _, base_path = init()
    if output_dir:
        media = Path(output_dir) / "media"
        excel = Path(output_dir) / "excel"
        media.mkdir(parents=True, exist_ok=True)
        excel.mkdir(parents=True, exist_ok=True)
        base_path = {"media": str(media), "excel": str(excel)}

    valid_choices = {
        "all",
        "media",
        "media-image",
        "media-video",
        "image-flat",
        "video-flat",
        "excel",
    }
    if save_choice not in valid_choices:
        raise typer.BadParameter("invalid save-choice")

    spider = Data_Spider(rate_limit=rate_limit)
    spider.spider_some_note([url], cookie, base_path, save_choice, excel_name, transcode=transcode)
    typer.echo(f"Crawled {url} successfully")

if __name__ == "__main__":
    app()
