import math
from typing import Dict, List, Tuple
from findex.index import InvertedIndex

class Ranker:
    def __init__(self, index: InvertedIndex):
        self.index = index
        self.N = index.doc_count
        self.avgdl = (
            sum(meta.length for meta in index.doc_metadata.values()) / self.N
            if self.N > 0 else 0
        )

    def idf(self, term: str) -> float:
        """Обчислення IDF (Inverse Document Frequency)."""
        df = len(self.index.index.get(term.lower(), []))
        if df == 0:
            return 0.0
        return math.log((self.N - df + 0.5) / (df + 0.5) + 1)

    def score_tf_idf(self, query: str) -> List[Tuple[int, float]]:
        """Ранжування за базовою моделлю TF-IDF."""
        terms = query.lower().split()
        scores: Dict[int, float] = {}
        for term in terms:
            postings = self.index.index.get(term, [])
            idf_val = self.idf(term)
            for p in postings:
                tf = p.tf / self.index.doc_metadata[p.doc_id].length
                scores[p.doc_id] = scores.get(p.doc_id, 0.0) + (tf * idf_val)
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def score_bm25(self, query: str, k1: float = 1.5, b: float = 0.75) -> List[Tuple[int, float]]:
        """Ранжування за алгоритмом Okapi BM25."""
        terms = query.lower().split()
        scores: Dict[int, float] = {}
        for term in terms:
            postings = self.index.index.get(term, [])
            idf_val = self.idf(term)
            for p in postings:
                doc_len = self.index.doc_metadata[p.doc_id].length
                tf = p.tf
                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * (doc_len / self.avgdl))
                score = idf_val * (numerator / denominator)
                scores[p.doc_id] = scores.get(p.doc_id, 0.0) + score
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
