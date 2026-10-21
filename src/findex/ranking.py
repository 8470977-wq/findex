import math
import numpy as np
from typing import List, Dict, Tuple
from findex.models import SearchResult, Posting
from findex.index import InvertedIndex

class Scorer:
    def score(self, query_terms: List[str], doc_id: int) -> float:
        raise NotImplementedError

class BM25Scorer(Scorer):
    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75) -> None:
        self.index = index
        self.k1 = k1
        self.b = b

    def score_fast(self, query_terms: List[str]) -> List[SearchResult]:
        """Оптимізоване векторне обчислення BM25 через NumPy."""
        scores: Dict[int, float] = {}
        N = self.index.num_docs
        avgdl = self.index.avg_doc_length or 1.0

        for term in query_terms:
            postings = self.index[term]
            if not postings:
                continue
            
            df = len(postings)
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1.0)
            
            doc_ids = np.array([p.doc_id for p in postings], dtype=np.int32)
            tfs = np.array([p.tf for p in postings], dtype=np.float32)
            lens = np.array([self.index.doc_metadata[d].length for d in doc_ids], dtype=np.float32)

            # Векторна формула BM25 через NumPy
            num = tfs * (self.k1 + 1.0)
            den = tfs + self.k1 * (1.0 - self.b + self.b * (lens / avgdl))
            term_scores = idf * (num / den)

            for d_id, s in zip(doc_ids, term_scores):
                scores[int(d_id)] = scores.get(int(d_id), 0.0) + float(s)

        results = [SearchResult(doc_id=d, score=s) for d, s in scores.items()]
        results.sort(key=lambda x: x.score, reverse=True)
        return results

class TfidfScorer(Scorer):
    def __init__(self, index: InvertedIndex) -> None:
        self.index = index

    def score_fast(self, query_terms: List[str]) -> List[SearchResult]:
        scores: Dict[int, float] = {}
        N = self.index.num_docs

        for term in query_terms:
            postings = self.index[term]
            if not postings:
                continue
            df = len(postings)
            idf = math.log((N + 1.0) / (df + 1.0)) + 1.0

            for p in postings:
                tf = math.log(1.0 + p.tf)
                scores[p.doc_id] = scores.get(p.doc_id, 0.0) + tf * idf

        results = [SearchResult(doc_id=d, score=s) for d, s in scores.items()]
        results.sort(key=lambda x: x.score, reverse=True)
        return results

class Ranker:
    def __init__(self, index: InvertedIndex) -> None:
        self.index = index

    def search(self, query: str, scorer: Scorer, top_k: int = 10) -> List[SearchResult]:
        from findex.corpus import tokenize
        terms = list(tokenize(query))
        if not terms:
            return []

        if isinstance(scorer, BM25Scorer):
            results = scorer.score_fast(terms)
        elif isinstance(scorer, TfidfScorer):
            results = scorer.score_fast(terms)
        else:
            results = []

        return results[:top_k]

def rrf_merge(lexical_results: List[SearchResult], semantic_results: List[SearchResult], k: int = 60) -> List[SearchResult]:
    """Reciprocal Rank Fusion (RRF) для об'єднання лексичних і семантичних результатів."""
    scores: Dict[int, float] = {}

    for rank, res in enumerate(lexical_results):
        scores[res.doc_id] = scores.get(res.doc_id, 0.0) + 1.0 / (k + rank + 1)

    for rank, res in enumerate(semantic_results):
        scores[res.doc_id] = scores.get(res.doc_id, 0.0) + 1.0 / (k + rank + 1)

    merged = [SearchResult(doc_id=d, score=s) for d, s in scores.items()]
    merged.sort(key=lambda x: x.score, reverse=True)
    return merged
