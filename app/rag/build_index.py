import os, pickle
from pathlib import Path

# Safe no-op index builder so Docker build doesn't fail before data exists.
INDEX_DIR = 'app/rag/index'
DATA_CSV  = 'app/data/space_weather.csv'

def main():
    os.makedirs(INDEX_DIR, exist_ok=True)
    # Create empty placeholder artifacts so later code can load them safely.
    # We skip sklearn here to keep the Docker build step fast and robust.
    Path(os.path.join(INDEX_DIR, "tfidf.pkl")).write_bytes(b"")
    Path(os.path.join(INDEX_DIR, "matrix.pkl")).write_bytes(b"")
    Path(os.path.join(INDEX_DIR, "meta.pkl")).write_bytes(b"")
    print("[build_index] Placeholder index files created.")

if __name__ == "__main__":
    main()
