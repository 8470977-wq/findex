import sys
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))

import pytest
from findex.index import InvertedIndex

def test_index_build(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    (d / "doc1.txt").write_text("apple banana apple", encoding="utf-8")
    (d / "doc2.txt").write_text("banana cherry", encoding="utf-8")

    idx = InvertedIndex()
    idx.build(d)

    assert len(idx.doc_metadata) == 2
    assert "apple" in idx.index
    assert len(idx.index["apple"]) == 1
    assert idx.index["apple"][0].tf == 2

def test_serialization(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    (d / "doc1.txt").write_text("hello world", encoding="utf-8")

    idx = InvertedIndex()
    idx.build(d)

    file_p = tmp_path / "index.bin"
    idx.save_pickle(file_p)
    loaded = InvertedIndex.load_pickle(file_p)
    assert "hello" in loaded.index
