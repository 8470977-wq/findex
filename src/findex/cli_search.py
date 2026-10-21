import argparse
import time
import tracemalloc
from findex.index import InvertedIndex
from findex.search import BooleanSearchEngine

def main():
    parser = argparse.ArgumentParser(description="Search in Inverted Index")
    parser.add_argument("index_path", type=str, help="Path to saved index file")
    parser.add_argument("query", type=str, help="Search terms (e.g. 'term1 term2')")
    parser.add_argument("--engine", choices=["merge", "set"], default="merge", help="Search engine")
    args = parser.parse_args()

    tracemalloc.start()
    start = time.perf_counter()

    idx = InvertedIndex.load_pickle(args.index_path)
    engine = BooleanSearchEngine(idx, engine=args.engine)
    terms = args.query.split()

    if len(terms) >= 2:
        res = engine.search_and(terms[0], terms[1])
    elif len(terms) == 1:
        res = [p.doc_id for p in idx.index.get(terms[0].lower(), [])]
    else:
        res = []

    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Results for '{args.query}': {res}")
    print(f"Time: {elapsed:.6f}s | Peak Memory: {peak / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()
