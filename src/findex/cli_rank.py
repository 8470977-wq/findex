import argparse
from pathlib import Path
from findex.index import open_index
from findex.ranking import Ranker, BM25Scorer, TfidfScorer

def main() -> None:
    parser = argparse.ArgumentParser(description="Ranked search in Inverted Index")
    parser.add_argument("index_path", type=str, help="Path to index file")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--method", choices=["tfidf", "bm25"], default="bm25", help="Ranking method")
    parser.add_argument("--top", type=int, default=5, help="Top N results")
    args = parser.parse_args()

    with open_index(Path(args.index_path)) as idx:
        ranker = Ranker(idx)
        scorer = BM25Scorer(idx) if args.method == "bm25" else TfidfScorer(idx)
        results = ranker.search(args.query, scorer, top_k=args.top)

        print(f"\nTop {args.top} results for '{args.query}' [{args.method.upper()}]:")
        for res in results:
            meta = idx.doc_metadata[res.doc_id]
            print(f"  Doc ID: {res.doc_id} | Score: {res.score:.4f} | Path: {meta.path}")

if __name__ == "__main__":
    main()
