"""Simplified Typer based command line interface."""

from typing import Optional
import os

import typer

from main import Data_Spider
from xhs_utils.common_util import init

app = typer.Typer(help="XHS Spider command line interface")

@app.command()
def version() -> None:
    """Show tool version."""
    typer.echo("xhs-spider 0.1")

@app.command()
def crawl(
    cookie: str = typer.Option(..., help="Xiaohongshu cookie"),
    note_id: str = typer.Option(..., help="Note ID to crawl"),
    save_choice: str = typer.Option("all", help="Save option"),
    excel_name: str = typer.Option("", help="Excel file name"),
    output_dir: Optional[str] = typer.Option(None, help="Directory to store output"),
    rate_limit: float = typer.Option(0.0, help="Delay between requests in seconds"),
    transcode: bool = typer.Option(False, help="Transcode videos to MP4"),
):
    """Crawl a single note and save data."""
    if not cookie.strip():
        raise typer.BadParameter("cookie cannot be empty")
    if not note_id.strip() or len(note_id) > 64:
        raise typer.BadParameter("note-id is invalid")
    if rate_limit < 0:
        raise typer.BadParameter("--rate-limit must be non-negative")
    if save_choice in ("excel", "all") and not excel_name:
        raise typer.BadParameter("--excel-name is required when --save-choice is excel or all")

    cookies_str, base_path = init()
    if output_dir:
        output_dir = os.path.abspath(output_dir)
        media = os.path.join(output_dir, "media")
        excel = os.path.join(output_dir, "excel")
        os.makedirs(media, exist_ok=True)
        os.makedirs(excel, exist_ok=True)
        base_path = {"media": media, "excel": excel}

    spider = Data_Spider(rate_limit=rate_limit)
    note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
    try:
        spider.spider_some_note([note_url], cookie, base_path, save_choice, excel_name, transcode=transcode)
    except ValueError as e:
        raise typer.BadParameter(str(e))

    typer.echo(f"Crawled {note_id} successfully")

if __name__ == "__main__":
    app()
