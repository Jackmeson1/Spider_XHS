import re
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
    cookie: str = typer.Option(..., help="Xiaohongshu cookie"),
    note_id: str = typer.Option(..., help="Note ID to crawl", callback=validate_note_id),
    rate_limit: float = typer.Option(0.0, help="Delay between requests in seconds"),
):
    """Crawl a single note."""
    if not cookie.strip():
        raise typer.BadParameter("cookie cannot be empty")

    _, base_path = init()
    spider = Data_Spider(rate_limit=rate_limit)
    note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
    success, msg, info = spider.spider_note(note_url, cookie)
    if success:
        typer.echo(f"Crawled {note_id} successfully")
    else:
        typer.echo(f"Failed: {msg}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
