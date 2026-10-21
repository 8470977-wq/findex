import re
import uuid
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends, Query, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from findex.index import InvertedIndex
from findex.ranking import Ranker, BM25Scorer, TfidfScorer
from findex.web.config import settings
from findex.web.schemas import SearchResponse, SearchResultItem, StatsResponse, DocResponse

logger = logging.getLogger("findex.web")

# Шукаємо папку templates поруч із файлом app.py
BASE_DIR = Path(__file__).resolve().parent
templates_dir = BASE_DIR / "templates"

if not templates_dir.exists():
    templates_dir.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(templates_dir))

index_instance: Optional[InvertedIndex] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global index_instance
    if settings.index_path.exists():
        try:
            index_instance = InvertedIndex.load_pickle(settings.index_path)
            logger.info(f"Індекс завантажено з {settings.index_path}")
        except Exception as e:
            logger.error(f"Помилка завантаження індексу: {e}")
            index_instance = None
    else:
        logger.warning(f"Файл індексу {settings.index_path} не знайдено.")
        index_instance = None
    yield

app = FastAPI(title=settings.app_name, lifespan=lifespan)

def get_index() -> InvertedIndex:
    if index_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Індекс ще не завантажений"
        )
    return index_instance

@app.middleware("http")
async def log_exceptions_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error(f"Request {request_id} failed: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Внутрішня помилка сервера", "request_id": request_id}
        )

@app.get("/health")
def health_check(index: InvertedIndex = Depends(get_index)):
    return {"status": "ok", "docs_count": index.num_docs}

@app.get("/stats", response_model=StatsResponse)
def get_stats(index: InvertedIndex = Depends(get_index)):
    return StatsResponse(
        num_terms=len(index),
        num_docs=index.num_docs,
        avg_doc_length=index.avg_doc_length
    )

@app.get("/search", response_model=SearchResponse)
def search_api(
    q: str = Query(..., min_length=1, description="Пошуковий запит"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    mode: str = Query("hybrid", pattern="^(lexical|semantic|hybrid)$"),
    index: InvertedIndex = Depends(get_index)
):
    ranker = Ranker(index)
    scorer = BM25Scorer(index)
    lexical_res = ranker.search(q, scorer, top_k=100)

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_results = lexical_res[start_idx:end_idx]

    items = []
    for res in page_results:
        meta = index.doc_metadata.get(res.doc_id)
        doc_path = meta.path if meta else "unknown"
        items.append(SearchResultItem(
            doc_id=res.doc_id,
            score=res.score,
            path=doc_path,
            snippet=f"Matched document #{res.doc_id}"
        ))

    return SearchResponse(
        query=q,
        total_results=len(lexical_res),
        page=page,
        page_size=page_size,
        results=items
    )

@app.get("/docs/{doc_id}", response_model=DocResponse)
def get_document(doc_id: int, index: InvertedIndex = Depends(get_index)):
    meta = index.doc_metadata.get(doc_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Документ #{doc_id} не знайдено")
    
    content = f"Вміст документа #{doc_id}"
    if meta and Path(meta.path).exists():
        try:
            content = Path(meta.path).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass
        
    return DocResponse(doc_id=doc_id, path=meta.path, content=content)

@app.get("/", response_class=HTMLResponse)
def home_page(request: Request, q: Optional[str] = None, index: InvertedIndex = Depends(get_index)):
    results = []
    total = 0
    if q:
        ranker = Ranker(index)
        scorer = BM25Scorer(index)
        search_res = ranker.search(q, scorer, top_k=10)
        total = len(search_res)

        for r in search_res:
            meta = index.doc_metadata.get(r.doc_id)
            content = f"Збіг у документі #{r.doc_id}"
            if meta and Path(meta.path).exists():
                try:
                    content = Path(meta.path).read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    pass

            snippet = content[:200]
            for word in q.split():
                snippet = re.sub(f"({re.escape(word)})", r"<mark>\1</mark>", snippet, flags=re.IGNORECASE)

            results.append({
                "doc_id": r.doc_id,
                "score": r.score,
                "snippet": snippet
            })

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "query": q or "", "results": results, "total": total}
    )
