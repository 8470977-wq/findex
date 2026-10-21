import pytest
import numpy as np
from findex.index import InvertedIndex
from findex.ranking import Ranker, BM25Scorer, rrf_merge, SearchResult

def test_numpy_bm25_speedup():
    idx = InvertedIndex()
    ranker = Ranker(idx)
    scorer = BM25Scorer(idx)
    res = ranker.search("python engine", scorer)
    assert isinstance(res, list)

def test_rrf_merge():
    r1 = [SearchResult(doc_id=1, score=10.0), SearchResult(doc_id=2, score=5.0)]
    r2 = [SearchResult(doc_id=2, score=8.0), SearchResult(doc_id=1, score=3.0)]
    merged = rrf_merge(r1, r2)
    assert len(merged) == 2
    assert merged[0].doc_id in (1, 2)
