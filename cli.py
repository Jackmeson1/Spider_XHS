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
    note_id: str = typer.Option(
        None,
        help="Note ID to crawl if --note-url is not provided (prefer passing the full note URL)",
    ),
    note_url: str = typer.Option(None, help="Full note URL to crawl (recommended)"),
    rate_limit: float = typer.Option(0.0, help="Delay between requests in seconds"),
):
    """Crawl a single note."""
    if not cookie.strip():
        raise typer.BadParameter("cookie cannot be empty")

    if note_url and note_url.strip():
        target_url = note_url.strip()
    else:
        if not note_id or not note_id.strip() or len(note_id) > 64:
            raise typer.BadParameter("note-id is invalid")
        target_url = f"https://www.xiaohongshu.com/explore/{note_id.strip()}"

    _, base_path = init()
    spider = Data_Spider(rate_limit=rate_limit)
    success, msg, info = spider.spider_note(target_url, cookie)
    if success:
        typer.echo(f"Crawled {note_url or note_id} successfully")
    else:
        typer.echo(f"Failed: {msg}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
