import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from findex.search.engine import search_query

app = FastAPI(title="findex")

# Визначення точного абсолютного шляху до директорії з шаблонами
BASE_DIR = Path(__file__).resolve().parent
templates_dir = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(templates_dir))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, q: str = ""):
    results = []
    if q:
        results = search_query("index.bin", q)
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
