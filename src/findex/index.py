import pickle
from pathlib import Path
from typing import Dict, List, Iterator, Any
from functools import cached_property
from collections.abc import Mapping
from contextlib import contextmanager
from findex.models import Posting, DocMeta

class InvertedIndex(Mapping):
    def __init__(self) -> None:
        self.index: Dict[str, List[Posting]] = {}
        self.doc_metadata: Dict[int, DocMeta] = {}
        self.doc_count: int = 0

    # Dunder-методи згідно з протоколом Mapping
    def __getitem__(self, term: str) -> List[Posting]:
        return self.index.get(term.lower(), [])

    def __len__(self) -> int:
        return len(self.index)

    def __iter__(self) -> Iterator[str]:
        return iter(self.index)

    def __contains__(self, term: object) -> bool:
        if isinstance(term, str):
            return term.lower() in self.index
        return False

    def __repr__(self) -> str:
        return f"<InvertedIndex terms={len(self.index)} docs={self.doc_count}>"

    @property
    def num_docs(self) -> int:
        return self.doc_count

    @cached_property
    def avg_doc_length(self) -> float:
        if self.doc_count == 0:
            return 0.0
        total_len = sum(meta.length for meta in self.doc_metadata.values())
        return total_len / self.doc_count

    def df(self, term: str) -> int:
        return len(self[term])

    def save_pickle(self, path: Path) -> None:
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load_pickle(cls, path: Path) -> "InvertedIndex":
        with open(path, "rb") as f:
            return pickle.load(f)

@contextmanager
def open_index(path: Path):
    """Context Manager для безпечного відкриття та звільнення ресурсів індексу."""
    idx = InvertedIndex.load_pickle(path)
    try:
        yield idx
    finally:
        del idx
