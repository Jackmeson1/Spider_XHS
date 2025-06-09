import typer
from main import Data_Spider
from xhs_utils.common_util import init

app = typer.Typer(help="XHS Spider command line interface")

@app.command()
def version() -> None:
    """Show tool version."""
    typer.echo("xhs-spider 0.1")

@app.command()
def crawl(cookie: str = typer.Option(..., help="Xiaohongshu cookie"),
          note_id: str = typer.Option(..., help="Note ID to crawl")):
    """Crawl a single note."""
    _, base_path = init()
    spider = Data_Spider()
    note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
    success, msg, info = spider.spider_note(note_url, cookie)
    if success:
        typer.echo(f"Crawled {note_id} successfully")
    else:
        typer.echo(f"Failed: {msg}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
