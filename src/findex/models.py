from dataclasses import dataclass
from typing import Optional

@dataclass
class Posting:
    doc_id: int
    tf: int

@dataclass
class DocMeta:
    doc_id: int
    path: str
    length: int

@dataclass
class SearchResult:
    doc_id: int
    score: float
    snippet: Optional[str] = None
