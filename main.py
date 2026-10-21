import sys
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))

from findex.stats import analyze_lazy, analyze_greedy

def main():
    data_dir = Path("data")
    print("[+] Lazy analysis...")
    lazy_res = analyze_lazy(data_dir)
    print(f"Lazy Time: {lazy_res['time_sec']:.4f}s | Peak Memory: {lazy_res['peak_memory_mb']:.2f} MB")

    print("[+] Greedy analysis...")
    greedy_res = analyze_greedy(data_dir)
    print(f"Greedy Time: {greedy_res['time_sec']:.4f}s | Peak Memory: {greedy_res['peak_memory_mb']:.2f} MB")

if __name__ == "__main__":
    main()
