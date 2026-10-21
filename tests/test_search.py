import sys
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))

import pytest
from findex.index import InvertedIndex
from findex.search import BooleanSearchEngine

def test_boolean_search(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    (d / "doc0.txt").write_text("cat dog", encoding="utf-8")
    (d / "doc1.txt").write_text("dog bird", encoding="utf-8")
    (d / "doc2.txt").write_text("cat bird", encoding="utf-8")

    idx = InvertedIndex()
    idx.build(d)

    engine_merge = BooleanSearchEngine(idx, engine="merge")
    engine_set = BooleanSearchEngine(idx, engine="set")

    # AND search
    assert engine_merge.search_and("cat", "dog") == [0]
    assert engine_set.search_and("cat", "dog") == [0]

    # OR search
    assert engine_merge.search_or("cat", "bird") == [0, 1, 2]
    assert engine_set.search_or("cat", "bird") == [0, 1, 2]

    # NOT search
    assert engine_merge.search_not("cat") == [1]
