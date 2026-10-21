import pickle
import re

def search_query(index_file: str, query: str):
    try:
        with open(index_file, 'rb') as f:
            data = pickle.load(f)
    except Exception:
        return []

    index = data.get('index', {})
    docs = data.get('docs', {})
    q_tokens = re.findall(r'\w+', query.lower())

    results = []
    for doc_id, doc_info in docs.items():
        content = doc_info['content']
        content_lower = content.lower()
        score = 0.0
        for t in q_tokens:
            score += content_lower.count(t)
        if score > 0:
            # Формування сніпету з підсвічуванням
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
