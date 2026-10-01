"""Shared representations for log anomaly detection.
Tier-1 Count  : per-session event-count vector (system-specific vocab)
Tier-3 Semantic: Template2Vec — word2vec over template words, TF-IDF weighted
                 session embedding in a SHARED space across systems.
"""
import os, json, re
import numpy as np

TOK = re.compile(r'[A-Za-z]+')

def tokenize(text):
    return [w.lower() for w in TOK.findall(text) if len(w) > 1 and w != 'blk']

def load_system(proc, name):
    counts = np.load(os.path.join(proc, f'{name}_counts.npy'))
    labels = np.load(os.path.join(proc, f'{name}_labels.npy')).astype(int)
    seqs = json.load(open(os.path.join(proc, f'{name}_seqs.json')))
    tpl = json.load(open(os.path.join(proc, f'{name}_templates.json')))
    return dict(name=name, counts=counts, labels=labels, seqs=seqs,
                templates=tpl['text'])

def train_template2vec(systems, dim=100, seed=1):
    """Train word2vec on the union of all template corpora -> shared word space."""
    from gensim.models import Word2Vec
    sentences = []
    for s in systems:
        for t in s['templates']:
            toks = tokenize(t)
            if toks:
                sentences.append(toks)
    w2v = Word2Vec(sentences, vector_size=dim, window=5, min_count=1,
                   workers=2, sg=1, epochs=30, seed=seed)
    return w2v

def template_embeddings(templates, w2v, dim):
    """Per-template vector = mean of its word vectors (idf-weighted)."""
    # idf over templates
    import math
    N = len(templates)
    dfc = {}
    toks_per = [tokenize(t) for t in templates]
    for toks in toks_per:
        for w in set(toks):
            dfc[w] = dfc.get(w, 0) + 1
    idf = {w: math.log((N + 1) / (c + 1)) + 1 for w, c in dfc.items()}
    E = np.zeros((len(templates), dim), dtype=np.float32)
    for i, toks in enumerate(toks_per):
        vs, ws = [], []
        for w in toks:
            if w in w2v.wv:
                vs.append(w2v.wv[w]); ws.append(idf.get(w, 1.0))
        if vs:
            E[i] = np.average(vs, axis=0, weights=ws)
    return E

def session_semantic(counts, tpl_emb):
    """Session embedding = count-weighted mean of template embeddings -> (N, dim)."""
    w = counts.astype(np.float32)
    denom = w.sum(1, keepdims=True); denom[denom == 0] = 1
    return (w @ tpl_emb) / denom
