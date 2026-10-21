import argparse
import time
import tracemalloc
from findex.index import InvertedIndex
from findex.ranking import Ranker

def main():
    parser = argparse.ArgumentParser(description="Ranked search in Inverted Index")
    parser.add_argument("index_path", type=str, help="Path to index file")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--method", choices=["tfidf", "bm25"], default="bm25", help="Ranking method")
    parser.add_argument("--top", type=int, default=5, help="Top N results")
    args = parser.parse_args()

    tracemalloc.start()
    start = time.perf_counter()

    idx = InvertedIndex.load_pickle(args.index_path)
    ranker = Ranker(idx)

    if args.method == "tfidf":
        results = ranker.score_tf_idf(args.query)[:args.top]
    else:
        results = ranker.score_bm25(args.query)[:args.top]

    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Top {args.top} results for '{args.query}' [{args.method.upper()}]:")
    for doc_id, score in results:
        meta = idx.doc_metadata[doc_id]
        print(f"  Doc ID: {doc_id} | Score: {score:.4f} | Path: {meta.path}")
    print(f"Time: {elapsed:.6f}s | Peak Memory: {peak / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()
