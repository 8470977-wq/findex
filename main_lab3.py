import sys
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))

from findex.index import InvertedIndex
from findex.ranking import Ranker

def main():
    data_dir = Path("data")
    idx = InvertedIndex()
    idx.build(data_dir)

    ranker = Ranker(idx)
    query = "python system"

    print("=== TF-IDF Results ===")
    for doc_id, score in ranker.score_tf_idf(query)[:3]:
        print(f"Doc {doc_id}: {score:.4f}")

    print("\n=== BM25 Results ===")
    for doc_id, score in ranker.score_bm25(query)[:3]:
        print(f"Doc {doc_id}: {score:.4f}")

if __name__ == "__main__":
    main()
