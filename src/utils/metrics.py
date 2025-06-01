def word_count_difference(doc1, doc2):
    """
    Returns the absolute and percentage difference in word count between two documents.
    """
    wc1 = len(doc1.split())
    wc2 = len(doc2.split())
    diff = abs(wc1 - wc2)
    percent = (diff / max(wc1, wc2)) * 100 if max(wc1, wc2) > 0 else 0
    return {"doc1_word_count": wc1, "doc2_word_count": wc2, "difference": diff, "percent_difference": round(percent, 2)}

def line_count_difference(doc1, doc2):
    """
    Returns the absolute and percentage difference in line count between two documents.
    """
    lc1 = len(doc1.splitlines())
    lc2 = len(doc2.splitlines())
    diff = abs(lc1 - lc2)
    percent = (diff / max(lc1, lc2)) * 100 if max(lc1, lc2) > 0 else 0
    return {"doc1_line_count": lc1, "doc2_line_count": lc2, "difference": diff, "percent_difference": round(percent, 2)}

def char_count_difference(doc1, doc2):
    """
    Returns the absolute and percentage difference in character count between two documents.
    """
    cc1 = len(doc1)
    cc2 = len(doc2)
    diff = abs(cc1 - cc2)
    percent = (diff / max(cc1, cc2)) * 100 if max(cc1, cc2) > 0 else 0
    return {"doc1_char_count": cc1, "doc2_char_count": cc2, "difference": diff, "percent_difference": round(percent, 2)}

def unique_word_ratio(doc):
    """
    Returns the ratio of unique words to total words in a document.
    """
    words = doc.split()
    if not words:
        return 0.0
    unique = set(words)
    return round(len(unique) / len(words), 3)

def jaccard_similarity(doc1, doc2):
    """
    Returns the Jaccard similarity between two documents (set of words).
    """
    set1 = set(doc1.lower().split())
    set2 = set(doc2.lower().split())
    intersection = set1 & set2
    union = set1 | set2
    return round(len(intersection) / len(union), 3) if union else 1.0

def cosine_similarity(doc1, doc2):
    """
    Returns the cosine similarity between two documents (bag-of-words).
    """
    from collections import Counter
    import math
    words1 = doc1.lower().split()
    words2 = doc2.lower().split()
    counter1 = Counter(words1)
    counter2 = Counter(words2)
    all_words = set(counter1) | set(counter2)
    v1 = [counter1.get(w, 0) for w in all_words]
    v2 = [counter2.get(w, 0) for w in all_words]
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return round(dot / (norm1 * norm2), 3)

def keyword_coverage(doc, keywords):
    """
    Returns the percentage of keywords present in the document.
    """
    doc_words = set(doc.lower().split())
    keywords = set(kw.lower() for kw in keywords)
    found = doc_words & keywords
    return round(100 * len(found) / len(keywords), 2) if keywords else 0.0

def get_all_metrics(doc1, doc2, keywords=None):
    """
    Returns a dictionary of all comparison metrics between two documents.
    """
    metrics = {}
    
    metrics["jaccard_similarity"] = jaccard_similarity(doc1, doc2)
    metrics["cosine_similarity"] = cosine_similarity(doc1, doc2)
    return metrics
