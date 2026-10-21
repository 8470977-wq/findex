import argparse
import time
import tracemalloc
from pathlib import Path
from findex.index import InvertedIndex

def main():
    parser = argparse.ArgumentParser(description="Build and save Inverted Index")
    parser.add_argument("data_dir", type=str, help="Path to data directory")
    parser.add_argument("--out", type=str, default="index.bin", help="Output index file path")
    args = parser.parse_args()

    tracemalloc.start()
    start = time.perf_counter()

    idx = InvertedIndex()
    idx.build(args.data_dir)
    idx.save_pickle(args.out)

    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"[+] Index built & saved to {args.out}")
    print(f"Time: {elapsed:.4f}s | Peak Memory: {peak / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()
