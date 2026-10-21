import pytest
from findex.index import InvertedIndex
from findex.ranking import Ranker, BM25Scorer, TfidfScorer

def test_bm25_ranking():
    idx = InvertedIndex()
    ranker = Ranker(idx)
    scorer = BM25Scorer(idx)
    results = ranker.search("test", scorer)
    assert isinstance(results, list)
