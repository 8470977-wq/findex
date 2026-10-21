import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from findex.search.engine import search_query

app = FastAPI(title="findex")

BASE_DIR = Path(__file__).resolve().parent
templates_dir = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

def get_index():
    """Допоміжна функція для імпорту в тестах"""
    return "index.bin"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, q: str = ""):
    results = []
    index_path = get_index()
    if q:
        results = search_query(index_path, q)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "query": q,
            "results": results,
            "total": len(results)
        }
    )

@app.get("/health")
async def health():
    return {"status": "ok"}
