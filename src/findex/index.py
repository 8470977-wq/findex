import pickle
import os
import psutil
from pathlib import Path
from typing import Dict, List, Iterator, Any, Tuple
from functools import cached_property
from collections.abc import Mapping
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from findex.models import Posting, DocMeta
from findex.corpus import tokenize

def build_partial(args: Tuple[List[Path], int]) -> Tuple[Dict[str, List[Posting]], Dict[int, DocMeta]]:
    """Функція рівня модуля для паралельної обробки шматка файлів (воркера)."""
    filepaths, start_doc_id = args
    partial_index: Dict[str, List[Posting]] = {}
    partial_meta: Dict[int, DocMeta] = {}

    for i, filepath in enumerate(filepaths):
        doc_id = start_doc_id + i
        text = filepath.read_text(encoding="utf-8", errors="ignore")
        tokens = list(tokenize(text))

        partial_meta[doc_id] = DocMeta(doc_id=doc_id, path=str(filepath), length=len(tokens))

        tf_counts: Dict[str, int] = {}
        for token in tokens:
            tf_counts[token] = tf_counts.get(token, 0) + 1

        for term, tf in tf_counts.items():
            if term not in partial_index:
                partial_index[term] = []
            partial_index[term].append(Posting(doc_id=doc_id, tf=tf))

    return partial_index, partial_meta

class InvertedIndex(Mapping):
    def __init__(self) -> None:
        self.index: Dict[str, List[Posting]] = {}
        self.doc_metadata: Dict[int, DocMeta] = {}
        self.doc_count: int = 0

    def merge(self, partials: List[Tuple[Dict[str, List[Posting]], Dict[int, DocMeta]]]) -> None:
        """Об'єднання часткових індексів від воркерів в один загальний індекс."""
        self.index.clear()
        self.doc_metadata.clear()
        self.doc_count = 0

        for p_index, p_meta in partials:
            self.doc_metadata.update(p_meta)
            for term, postings in p_index.items():
                if term not in self.index:
                    self.index[term] = []
                self.index[term].extend(postings)

        self.doc_count = len(self.doc_metadata)

    def build(self, data_dir: Path, workers: int = 1, executor_type: str = "serial") -> None:
        """Побудова індексу з підтримкою послідовного та паралельного виконання."""
        files = sorted(list(data_dir.glob("*.txt")))
        if not files:
            return

        workers = max(1, workers)
        chunk_size = (len(files) + workers - 1) // workers
        chunks = []

        for i in range(0, len(files), chunk_size):
            chunk_files = files[i:i + chunk_size]
            chunks.append((chunk_files, i))

        if executor_type == "serial" or workers == 1:
            partials = [build_partial(chunk) for chunk in chunks]
        elif executor_type == "threads":
            with ThreadPoolExecutor(max_workers=workers) as executor:
                partials = list(executor.map(build_partial, chunks))
        elif executor_type == "processes":
            with ProcessPoolExecutor(max_workers=workers) as executor:
                partials = list(executor.map(build_partial, chunks))
        else:
            raise ValueError(f"Unknown executor_type: {executor_type}")

        self.merge(partials)

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
