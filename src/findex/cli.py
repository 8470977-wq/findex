import argparse
import sys
import time
import tracemalloc
from pathlib import Path
from findex.index import InvertedIndex
from findex.search import BooleanSearchEngine
from findex.ranking import Ranker

def main() -> None:
    parser = argparse.ArgumentParser(prog="findex", description="findex Search Engine CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Команда: findex index <data_dir> --out <index_file>
    index_parser = subparsers.add_parser("index", help="Build and save inverted index")
    index_parser.add_argument("data_dir", type=str, help="Path to directory with documents")
    index_parser.add_argument("--out", type=str, default="index.bin", help="Output index file path")

    # Команда: findex search <index_file> "query" [--engine {merge,set}]
    search_parser = subparsers.add_parser("search", help="Perform boolean search")
    search_parser.add_argument("index_path", type=str, help="Path to saved index file")
    search_parser.add_argument("query", type=str, help="Search query")
    search_parser.add_argument("--engine", choices=["merge", "set"], default="merge", help="Search engine")

    # Команда: findex rank <index_file> "query" [--method {tfidf,bm25}] [--top N]
    rank_parser = subparsers.add_parser("rank", help="Perform ranked search")
    rank_parser.add_argument("index_path", type=str, help="Path to saved index file")
    rank_parser.add_argument("query", type=str, help="Search query")
    rank_parser.add_argument("--method", choices=["tfidf", "bm25"], default="bm25", help="Ranking method")
    rank_parser.add_argument("--top", type=int, default=5, help="Top N results")

    args = parser.parse_args()

    tracemalloc.start()
    start = time.perf_counter()

    if args.command == "index":
        idx = InvertedIndex()
        idx.build(Path(args.data_dir))
        idx.save_pickle(Path(args.out))
        print(f"[+] Index successfully built and saved to '{args.out}'")

    elif args.command == "search":
        idx = InvertedIndex.load_pickle(Path(args.index_path))
        engine = BooleanSearchEngine(idx, engine=args.engine)
        terms = args.query.split()
        if len(terms) >= 2:
            res = engine.search_and(terms[0], terms[1])
        elif len(terms) == 1:
            res = [p.doc_id for p in idx.index.get(terms[0].lower(), [])]
        else:
            res = []
        print(f"Results for '{args.query}' [{args.engine}]: {res}")

    elif args.command == "rank":
        idx = InvertedIndex.load_pickle(Path(args.index_path))
        ranker = Ranker(idx)
        if args.method == "tfidf":
            results = ranker.score_tf_idf(args.query)[:args.top]
        else:
            results = ranker.score_bm25(args.query)[:args.top]
        print(f"Top {args.top} results for '{args.query}' [{args.method.upper()}]:")
        for doc_id, score in results:
            meta = idx.doc_metadata[doc_id]
            print(f"  Doc ID: {doc_id} | Score: {score:.4f} | Path: {meta.path}")

    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Execution time: {elapsed:.6f}s | Peak Memory: {peak / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()
