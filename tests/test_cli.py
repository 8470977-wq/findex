import sys
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))

import pytest
from findex.index import InvertedIndex
from findex.search import BooleanSearchEngine
from findex.ranking import Ranker

def test_full_pipeline(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "doc0.txt").write_text("python search engine", encoding="utf-8")
    (data_dir / "doc1.txt").write_text("python programming language", encoding="utf-8")

    index_file = tmp_path / "index.bin"
    
    # 1. Test Indexing
    idx = InvertedIndex()
    idx.build(data_dir)
    idx.save_pickle(index_file)
    assert index_file.exists()

    # 2. Test Search
    loaded_idx = InvertedIndex.load_pickle(index_file)
    engine = BooleanSearchEngine(loaded_idx, engine="merge")
    res = engine.search_and("python", "search")
    assert res == [0]

    # 3. Test Ranking
    ranker = Ranker(loaded_idx)
    ranked_res = ranker.score_bm25("python")
    assert len(ranked_res) == 2
