import math
import time
import heapq
from functools import wraps, lru_cache
from typing import List, Tuple, Dict, Any, Protocol
from dataclasses import dataclass
from findex.index import InvertedIndex

def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        res = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[TIMED] Function '{func.__name__}' executed in {elapsed:.6f}s")
        return res
    return wrapper

@dataclass(order=True)
class SearchResult:
    score: float
    doc_id: int

class Scorer(Protocol):
    def score(self, term: str, tf: int, doc_len: int) -> float: ...

class TfidfScorer:
    def __init__(self, index: InvertedIndex) -> None:
        self.index = index
        self.N = index.num_docs

    def score(self, term: str, tf: int, doc_len: int) -> float:
        df = self.index.df(term)
        if df == 0 or doc_len == 0:
            return 0.0
        idf = math.log((self.N / df) + 1)
        term_tf = tf / doc_len
        return term_tf * idf

class BM25Scorer:
    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75) -> None:
        self.index = index
        self.N = index.num_docs
        self.k1 = k1
        self.b = b
        self.avgdl = index.avg_doc_length

    def score(self, term: str, tf: int, doc_len: int) -> float:
        df = self.index.df(term)
        if df == 0:
            return 0.0
        idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1)
        numerator = tf * (self.k1 + 1)
        denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / (self.avgdl or 1.0)))
        return idf * (numerator / denominator)

class Ranker:
    def __init__(self, index: InvertedIndex) -> None:
        self.index = index

    @timed
    def search(self, query: str, scorer: Scorer, top_k: int = 5) -> List[SearchResult]:
        terms = query.lower().split()
        scores: Dict[int, float] = {}

        for term in terms:
            postings = self.index[term]
            for p in postings:
                doc_len = self.index.doc_metadata[p.doc_id].length
                term_score = scorer.score(term, p.tf, doc_len)
                scores[p.doc_id] = scores.get(p.doc_id, 0.0) + term_score

        # Використовуємо heapq.nlargest для ефективного вибору топ-K
        heap = [SearchResult(score=score, doc_id=doc_id) for doc_id, score in scores.items()]
        return heapq.nlargest(top_k, heap)

@lru_cache(maxsize=128)
def cached_search(query: str, index_path_str: str, method: str = "bm25") -> List[Tuple[int, float]]:
    from pathlib import Path
    idx = InvertedIndex.load_pickle(Path(index_path_str))
    ranker = Ranker(idx)
    scorer = BM25Scorer(idx) if method == "bm25" else TfidfScorer(idx)
    results = ranker.search(query, scorer)
    return [(r.doc_id, r.score) for r in results]
