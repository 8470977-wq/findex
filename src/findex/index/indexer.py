import os
import re
import pickle

class InvertedIndex:
    def __init__(self):
        self.index = {}
        self.docs = {}

    def add_document(self, doc_id: int, content: str):
        self.docs[doc_id] = {'content': content}
        tokens = re.findall(r'\w+', content.lower())
        for token in tokens:
            if token not in self.index:
                self.index[token] = set()
            self.index[token].add(doc_id)

    def save(self, output_file: str):
        with open(output_file, 'wb') as f:
            pickle.dump({'index': self.index, 'docs': self.docs}, f)

    @classmethod
    def load(cls, index_file: str):
        inv = cls()
        with open(index_file, 'rb') as f:
            data = pickle.load(f)
            inv.index = data.get('index', {})
            inv.docs = data.get('docs', {})
        return inv

def build_index(data_dir: str, output_file: str):
    inv = InvertedIndex()
    doc_id = 1
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.txt'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                inv.add_document(doc_id, content)
                doc_id += 1
    inv.save(output_file)
    print(f"Успішно! Індекс збережено у '{output_file}'. Документів: {len(inv.docs)}")
