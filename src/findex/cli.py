import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from findex.index import InvertedIndex
from findex.search import BooleanSearchEngine
from findex.ranking import Ranker, BM25Scorer, TfidfScorer
from findex.crawler import async_crawl

app = typer.Typer(help="findex — CLI пошукова система")
console = Console()
err_console = Console(stderr=True)

def setup_logging(verbose: int) -> None:
    if verbose == 1:
        log_level = logging.INFO
    elif verbose >= 2:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s", stream=sys.stderr)

@app.callback()
def main_callback(
    verbose: int = typer.Option(0, "--verbose", "-v", count=True, help="Рівень логування (-v або -vv)")
) -> None:
    setup_logging(verbose)

@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Хост веб-сервера"),
    port: int = typer.Option(8000, "--port", "-p", help="Порт веб-сервера"),
    workers: int = typer.Option(1, "--workers", "-w", help="Кількість uvicorn воркерів"),
    index_path: Path = typer.Option(Path("index.bin"), "--index", "-i", help="Шлях до файлу індексу")
) -> None:
    """Запуск FastAPI веб-сервера утиліти findex."""
    import uvicorn
    import os
    os.environ["FINDEX_INDEX_PATH"] = str(index_path)
    console.print(f"[bold green]Запуск веб-сервера на http://{host}:{port}...[/bold green]")
    uvicorn.run("findex.web.app:app", host=host, port=port, workers=workers)

@app.command()
def crawl(
    start_url: str = typer.Argument(..., help="Початковий URL для краулінгу"),
    max_pages: int = typer.Option(200, "--max-pages", "-m", help="Максимальна кількість сторінок"),
    concurrency: int = typer.Option(5, "--concurrency", "-c", help="Кількість одночасних запитів"),
    out: Path = typer.Option(Path("crawled.jsonl"), "--out", "-o", help="Файл для збереження JSONL"),
    log_file: Path = typer.Option(Path("crawl.log"), "--log", "-l", help="Файл логу збоїв та статусу")
) -> None:
    """Асинхронний краулінг веб-сайту."""
    if out.exists():
        out.unlink()
    if log_file.exists():
        log_file.unlink()

    async def _run():
        count = 0
        console.print(f"[bold cyan]Запуск краулінгу {start_url} (concurrency={concurrency}, max_pages={max_pages})...[/bold cyan]")
        async for doc in async_crawl(start_url, max_pages=max_pages, concurrency=concurrency, out_jsonl=out, log_file=log_file):
            count += 1
            if count % 10 == 0 or count == max_pages:
                console.print(f"[green]Зібрано сторінок:[/green] {count}/{max_pages}")
        console.print(f"[bold green]Завершено![/bold green] Збережено {count} сторінок у '{out}'.")

    asyncio.run(_run())

@app.command()
def index(
    data_dir: Path = typer.Argument(..., help="Шлях до каталогу з документами"),
    out: Path = typer.Option(Path("index.bin"), "--out", "-o", help="Шлях збереження індексу"),
    workers: int = typer.Option(1, "--workers", "-w", help="Кількість паралельних воркерів"),
    executor: str = typer.Option("serial", "--executor", "-e", help="Тип виконання: serial, threads, processes")
) -> None:
    """Побудова та збереження інвертованого індексу з підтримкою паралелізму."""
    if not data_dir.exists():
        err_console.print(f"[bold red]Помилка:[/bold red] Каталог '{data_dir}' не існує.")
        raise typer.Exit(code=1)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description=f"Побудова індексу ({executor}, workers={workers})...", total=None)
        idx = InvertedIndex()
        idx.build(data_dir, workers=workers, executor_type=executor)
        idx.save_pickle(out)

    console.print(f"[bold green]Успішно![/bold green] Індекс збережено у '{out}'. Документів: {idx.num_docs}")

@app.command()
def search(
    index_path: Path = typer.Argument(..., help="Шлях до файлу індексу"),
    query: str = typer.Argument(..., help="Пошуковий запит"),
    method: str = typer.Option("bm25", "--method", "-m", help="Метод ранжування: bm25 або tfidf"),
    json_out: bool = typer.Option(False, "--json", help="Вивід результатів у форматі JSON в stdout"),
    top: int = typer.Option(5, "--top", "-t", help="Кількість топ-результатів")
) -> None:
    """Ранжований пошук у побудованому індексі."""
    if not index_path.exists():
        err_console.print(f"[bold red]Помилка:[/bold red] Файл індексу '{index_path}' не знайдено.")
        raise typer.Exit(code=1)

    try:
        idx = InvertedIndex.load_pickle(index_path)
        ranker = Ranker(idx)
        scorer = BM25Scorer(idx) if method == "bm25" else TfidfScorer(idx)
        results = ranker.search(query, scorer, top_k=top)

        if json_out:
            output = [{"doc_id": r.doc_id, "score": round(r.score, 4)} for r in results]
            print(json.dumps(output, indent=2))
        else:
            table = Table(title=f"Результати пошуку для '{query}' ({method.upper()})")
            table.add_column("Doc ID", justify="right", style="cyan")
            table.add_column("Score", justify="right", style="magenta")
            table.add_column("Шлях до файлу", style="green")

            for res in results:
                meta = idx.doc_metadata[res.doc_id]
                table.add_row(str(res.doc_id), f"{res.score:.4f}", str(meta.path))

            console.print(table)
    except Exception as e:
        err_console.print(f"[bold red]Помилка виконання пошуку:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def stats(
    index_path: Path = typer.Argument(..., help="Шлях до файлу індексу")
) -> None:
    """Вивід статистики індексу."""
    if not index_path.exists():
        err_console.print(f"[bold red]Помилка:[/bold red] Файл індексу '{index_path}' не знайдено.")
        raise typer.Exit(code=1)

    idx = InvertedIndex.load_pickle(index_path)
    console.print(f"[bold cyan]Кількість термінів:[/bold cyan] {len(idx)}")
    console.print(f"[bold cyan]Кількість документів:[/bold cyan] {idx.num_docs}")
    console.print(f"[bold cyan]Середня довжина документа:[/bold cyan] {idx.avg_doc_length:.2f}")

if __name__ == "__main__":
    app()
