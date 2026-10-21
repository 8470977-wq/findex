import pickle
import re

class SearchEngine:
    def __init__(self, index_file: str = "index.bin"):
        self.index_file = index_file

    def search(self, query: str):
        return search_query(self.index_file, query)

def search_query(index_file: str, query: str):
    try:
        with open(index_file, 'rb') as f:
            data = pickle.load(f)
    except Exception:
        return []
    
    docs = data.get('docs', {})
    q_tokens = re.findall(r'\w+', query.lower())
    
    results = []
    for doc_id, doc_info in docs.items():
        content = doc_info.get('content', '')
        content_lower = content.lower()
        score = 0.0
        for t in q_tokens:
            score += content_lower.count(t)
        if score > 0:
            snippet = content[:200]
            for t in q_tokens:
                pattern = re.compile(re.escape(t), re.IGNORECASE)
                snippet = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", snippet)
            results.append({
                'doc_id': doc_id,
                'score': score,
                'snippet': snippet
            })
    results.sort(key=lambda x: x['score'], reverse=True)
    return results
