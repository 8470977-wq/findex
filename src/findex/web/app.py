from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from findex.search.engine import search_query
import os

app = FastAPI(title="findex")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, q: str = ""):
    results = []
    if q:
        results = search_query("index.bin", q)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "query": q,
        "results": results,
        "total": len(results)
    })

@app.get("/health")
async def health():
    return {"status": "ok"}
