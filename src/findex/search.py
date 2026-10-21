from typing import List, Set
from findex.index import InvertedIndex


class BooleanSearchEngine:
    def __init__(self, index: InvertedIndex, engine: str = "merge"):
        if engine not in ("merge", "set"):
            raise ValueError("Engine must be 'merge' or 'set'")
        self.index = index
        self.engine = engine

    def _intersect_merge(self, list1: List[int], list2: List[int]) -> List[int]:
        """Двовказівниковий алгоритм перетину двох відсортованих списків (AND)."""
        res = []
        i, j = 0, 0
        while i < len(list1) and j < len(list2):
            if list1[i] == list2[j]:
                res.append(list1[i])
                i += 1
                j += 1
            elif list1[i] < list2[j]:
                i += 1
            else:
                j += 1
        return res

    def _union_merge(self, list1: List[int], list2: List[int]) -> List[int]:
        """Об'єднання двох відсортованих списків (OR)."""
        res = []
        i, j = 0, 0
        while i < len(list1) and j < len(list2):
            if list1[i] == list2[j]:
                res.append(list1[i])
                i += 1
                j += 1
            elif list1[i] < list2[j]:
                res.append(list1[i])
                i += 1
            else:
                res.append(list2[j])
                j += 1
        while i < len(list1):
            res.append(list1[i])
            i += 1
        while j < len(list2):
            res.append(list2[j])
            j += 1
        return res

    def search_and(self, term1: str, term2: str) -> List[int]:
        docs1 = [p.doc_id for p in self.index.index.get(term1.lower(), [])]
        docs2 = [p.doc_id for p in self.index.index.get(term2.lower(), [])]

        if self.engine == "merge":
            return self._intersect_merge(docs1, docs2)
        else:
            return sorted(list(set(docs1).intersection(set(docs2))))

    def search_or(self, term1: str, term2: str) -> List[int]:
        docs1 = [p.doc_id for p in self.index.index.get(term1.lower(), [])]
        docs2 = [p.doc_id for p in self.index.index.get(term2.lower(), [])]

        if self.engine == "merge":
            return self._union_merge(docs1, docs2)
        else:
            return sorted(list(set(docs1).union(set(docs2))))

    def search_not(self, term: str) -> List[int]:
        all_docs = set(self.index.doc_metadata.keys())
        term_docs = set(p.doc_id for p in self.index.index.get(term.lower(), []))
        return sorted(list(all_docs.difference(term_docs)))
