import array
import sys
import time
import tracemalloc
from pathlib import Path

sys.path.insert(0, str(Path("src").resolve()))

from findex.corpus import iter_documents, tokenize
from findex.index import InvertedIndex


class StandardPosting:
    def __init__(self, doc_id, tf):
        self.doc_id = doc_id
        self.tf = tf


def measure_storage_variants(data_dir):
    print("=== Порівняння структур даних для постінгів ===")
    
    # 1. Standard Objects
    tracemalloc.start()
    idx_std = {}
    for doc_id, (_, content) in enumerate(iter_documents(data_dir)):
        for token in tokenize(content):
            if token not in idx_std:
                idx_std[token] = []
            idx_std[token].append(StandardPosting(doc_id, 1))
    _, peak_std = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # 2. Dataclass with slots=True
    tracemalloc.start()
    idx_slots = InvertedIndex()
    idx_slots.build(data_dir)
    _, peak_slots = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # 3. Compact array('I')
    tracemalloc.start()
    idx_array = {}
    for doc_id, (_, content) in enumerate(iter_documents(data_dir)):
        for token in tokenize(content):
            if token not in idx_array:
                idx_array[token] = array.array("I")
            idx_array[token].extend([doc_id, 1])
    _, peak_array = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"1. Standard Class:   Peak Memory = {peak_std / (1024*1024):.2f} MB")
    print(f"2. Slots Dataclass:  Peak Memory = {peak_slots / (1024*1024):.2f} MB")
    print(f"3. array('I'):        Peak Memory = {peak_array / (1024*1024):.2f} MB")


if __name__ == "__main__":
    data_dir = Path("data")
    measure_storage_variants(data_dir)
