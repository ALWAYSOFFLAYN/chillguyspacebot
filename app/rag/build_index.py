import os, pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from app.config import DATA_CSV, INDEX_DIR

def main():
    df = pd.read_csv(DATA_CSV)
    df = df[df["text"].fillna("").str.strip() != ""]
    if df.empty:
        print("[build_index] No rows with text; skipping.")
        return

    os.makedirs(INDEX_DIR, exist_ok=True)
    vec = TfidfVectorizer(ngram_range=(1,2), max_features=30000)
    X = vec.fit_transform(df["text"].tolist())

    with open(os.path.join(INDEX_DIR, "tfidf.pkl"), "wb") as f: pickle.dump(vec, f)
    with open(os.path.join(INDEX_DIR, "matrix.pkl"), "wb") as f: pickle.dump(X, f)
    df.to_pickle(os.path.join(INDEX_DIR, "meta.pkl"))

    print(f"[build_index] rows={len(df)} vocab={len(vec.vocabulary_)} shape={X.shape}")

if __name__ == "__main__":
    main()
