import os, pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from app.config import INDEX_DIR

VEC = None
MAT = None
META = None

def _paths():
    return (
        os.path.join(INDEX_DIR, "tfidf.pkl"),
        os.path.join(INDEX_DIR, "matrix.pkl"),
        os.path.join(INDEX_DIR, "meta.pkl"),
    )

def _load_artifacts():
    global VEC, MAT, META
    tfidf, matrix, meta = _paths()
    with open(tfidf, "rb") as f: VEC = pickle.load(f)
    with open(matrix, "rb") as f: MAT = pickle.load(f)
    META = pd.read_pickle(meta)

def _ensure_loaded():
    global VEC, MAT, META
    if VEC is not None and MAT is not None and META is not None:
        return
    tfidf, matrix, meta = _paths()
    try:
        _load_artifacts()
    except FileNotFoundError:
        # Build index on the fly if it doesn't exist
        from app.rag.build_index import main as build_index
        print("[retriever] Index missing. Building now...")
        build_index()
        _load_artifacts()

def retrieve(query: str, k: int = 3):
    if not query:
        return []
    _ensure_loaded()
    qv = VEC.transform([query])
    sims = cosine_similarity(qv, MAT).ravel()
    top = sims.argsort()[::-1][:k]
    return [META.iloc[i]["text"] for i in top]
