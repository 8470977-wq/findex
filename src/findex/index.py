import pickle
from pathlib import Path
from typing import Dict, List, Iterator, Any
from functools import cached_property
from collections.abc import Mapping
from contextlib import contextmanager

from findex.models import Posting, DocMeta
from findex.corpus import tokenize

class InvertedIndex(Mapping):
    def __init__(self) -> None:
        self.index: Dict[str, List[Posting]] = {}
        self.doc_metadata: Dict[int, DocMeta] = {}
        self.doc_count: int = 0

    def build(self, data_dir: Path) -> None:
        """Побудова інвертованого індексу з текстових файлів у директорії."""
        self.index.clear()
        self.doc_metadata.clear()
        self.doc_count = 0

        files = sorted(list(data_dir.glob("*.txt")))
        for doc_id, filepath in enumerate(files):
            text = filepath.read_text(encoding="utf-8", errors="ignore")
            tokens = list(tokenize(text))
            
            # Сохраняем метаданные документа
            self.doc_metadata[doc_id] = DocMeta(doc_id=doc_id, path=str(filepath), length=len(tokens))
            
            # Подсчитываем частоты терминов (tf)
            tf_counts: Dict[str, int] = {}
            for token in tokens:
                tf_counts[token] = tf_counts.get(token, 0) + 1
                
            # Заполняем индекс
            for term, tf in tf_counts.items():
                if term not in self.index:
                    self.index[term] = []
                self.index[term].append(Posting(doc_id=doc_id, tf=tf))
                
            self.doc_count += 1

    # Dunder-методи
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
    idx = InvertedIndex.load_pickle(path)
    try:
        yield idx
    finally:
        del idx
