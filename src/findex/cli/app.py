import typer
from findex.index.indexer import build_index
import uvicorn

app = typer.Typer()

@app.command()
def index(data_dir: str = typer.Argument("data"), out: str = typer.Option("index.bin", "--out")):
    build_index(data_dir, out)

@app.command()
def serve(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run("findex.web.app:app", host=host, port=port)

if __name__ == "__main__":
    app()
