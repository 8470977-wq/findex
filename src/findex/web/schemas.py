from typing import List, Optional
from pydantic import BaseModel, Field

class SearchResultItem(BaseModel):
    doc_id: int
    score: float
    path: str
    snippet: str

class SearchResponse(BaseModel):
    query: str
    total_results: int
    page: int
    page_size: int
    results: List[SearchResultItem]

class StatsResponse(BaseModel):
    num_terms: int
    num_docs: int
    avg_doc_length: float

class DocResponse(BaseModel):
    doc_id: int
    path: str
    content: str
