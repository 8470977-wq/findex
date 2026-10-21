import sys
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))

import pytest
from findex.index import InvertedIndex
from findex.ranking import Ranker

def test_bm25_ranking(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    (d / "doc0.txt").write_text("apple apple banana", encoding="utf-8")
    (d / "doc1.txt").write_text("apple cherry", encoding="utf-8")

    idx = InvertedIndex()
    idx.build(d)

    ranker = Ranker(idx)
    res = ranker.score_bm25("apple")
    
    assert len(res) == 2
    # doc0 має вищий TF для "apple"
    assert res[0][0] == 0
