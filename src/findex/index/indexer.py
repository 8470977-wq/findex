import os
import re
import pickle

def tokenize(text: str):
    return re.findall(r'\w+', text.lower())

def build_index(data_dir: str, output_file: str):
    index = {}
    docs = {}
    doc_id = 1
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.txt'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                docs[doc_id] = {'path': path, 'content': content}
                tokens = tokenize(content)
                for token in tokens:
                    if token not in index:
                        index[token] = set()
                    index[token].add(doc_id)
                doc_id += 1
    with open(output_file, 'wb') as f:
        pickle.dump({'index': index, 'docs': docs}, f)
    print(f"Успішно! Індекс збережено у '{output_file}'. Документів: {len(docs)}")
