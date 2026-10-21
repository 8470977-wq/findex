import array
import json
import pickle
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Union

from findex.corpus import iter_documents, tokenize
from findex.models import DocMeta, Posting


class InvertedIndex:
    def __init__(self, store_positions: bool = False):
        self.store_positions = store_positions
        # term -> list of Posting
        self.index: Dict[str, List[Posting]] = defaultdict(list)
        # doc_id -> DocMeta
        self.doc_metadata: Dict[int, DocMeta] = {}
        self.doc_count = 0

    def build(self, data_dir: Union[str, Path]) -> None:
        """Будує інвертований індекс за один прохід по лінивому пайплайну."""
        data_path = Path(data_dir)
        for doc_id, (file_path, content) in enumerate(iter_documents(data_path)):
            tokens = list(tokenize(content))
            doc_len = len(tokens)
            self.doc_metadata[doc_id] = DocMeta(
                doc_id=doc_id, path=str(file_path), length=doc_len
            )

            if self.store_positions:
                term_positions = defaultdict(list)
                for pos, token in enumerate(tokens):
                    term_positions[token].append(pos)
                for token, positions in term_positions.items():
                    self.index[token].append(
                        Posting(doc_id=doc_id, tf=len(positions), positions=positions)
                    )
            else:
                counts = Counter(tokens)
                for token, count in counts.items():
                    self.index[token].append(Posting(doc_id=doc_id, tf=count))

            self.doc_count += 1

    def save_pickle(self, filepath: Union[str, Path]) -> None:
        """Збереження через pickle."""
        with open(filepath, "wb") as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_pickle(filepath: Union[str, Path]) -> "InvertedIndex":
        """Завантаження з pickle.
        
        УВАГА: pickle.load небезпечний для чужих файлів, оскільки може виконувати
        довільний Python-код під час десеріалізації (через __reduce__).
        """
        with open(filepath, "rb") as f:
            return pickle.load(f)

    def save_json(self, filepath: Union[str, Path]) -> None:
        """Альтернативна серіалізація у формат JSON."""
        data = {
            "store_positions": self.store_positions,
            "doc_count": self.doc_count,
            "metadata": {
                str(k): {"doc_id": v.doc_id, "path": v.path, "length": v.length}
                for k, v in self.doc_metadata.items()
            },
            "index": {
                term: [
                    {"doc_id": p.doc_id, "tf": p.tf, "positions": p.positions}
                    for p in postings
                ]
                for term, postings in self.index.items()
            },
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    @staticmethod
    def load_json(filepath: Union[str, Path]) -> "InvertedIndex":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        idx = InvertedIndex(store_positions=data["store_positions"])
        idx.doc_count = data["doc_count"]
        idx.doc_metadata = {
            int(k): DocMeta(**v) for k, v in data["metadata"].items()
        }
        for term, postings in data["index"].items():
            idx.index[term] = [Posting(**p) for p in postings]
        return idx
