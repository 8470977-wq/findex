import time
import tracemalloc
from collections import Counter
from pathlib import Path
from typing import Dict, Any
from findex.corpus import iter_documents, tokenize

def analyze_lazy(data_dir: Path) -> Dict[str, Any]:
    tracemalloc.start()
    start_time = time.perf_counter()

    doc_count = 0
    token_count = 0
    vocab = Counter()

    for _, content in iter_documents(data_dir):
        doc_count += 1
        for token in tokenize(content):
            token_count += 1
            vocab[token] += 1

    elapsed_time = time.perf_counter() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "doc_count": doc_count,
        "token_count": token_count,
        "vocab_size": len(vocab),
        "top_50": vocab.most_common(50),
        "time_sec": elapsed_time,
        "peak_memory_mb": peak_memory / (1024 * 1024),
    }

def analyze_greedy(data_dir: Path) -> Dict[str, Any]:
    tracemalloc.start()
    start_time = time.perf_counter()

    all_docs = [
        path.read_text(encoding="utf-8")
        for path in Path(data_dir).rglob("*.txt")
        if path.is_file()
    ]

    all_tokens = []
    for doc in all_docs:
        all_tokens.extend(list(tokenize(doc)))

    doc_count = len(all_docs)
    token_count = len(all_tokens)
    vocab = Counter(all_tokens)

    elapsed_time = time.perf_counter() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "doc_count": doc_count,
        "token_count": token_count,
        "vocab_size": len(vocab),
        "top_50": vocab.most_common(50),
        "time_sec": elapsed_time,
        "peak_memory_mb": peak_memory / (1024 * 1024),
    }
