import os
from typing import List, Dict

def load_texts(data_dir: str = "../data") -> List[Dict]:
    """
    Load all .txt files from data_dir and return a list of dicts:
    [{"id": "<filename>", "text": "<file contents>"}]
    """
    docs = []
    data_dir = os.path.abspath(data_dir)
    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"data directory not found: {data_dir}")
    for fname in sorted(os.listdir(data_dir)):
        if not fname.lower().endswith(".txt"):
            continue
        path = os.path.join(data_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        docs.append({"id": fname, "text": text})
    return docs

if __name__ == "__main__":
    base = os.path.dirname(__file__)
    docs = load_texts(os.path.join(base, "..", "data"))
    print(f"Loaded {len(docs)} text files from data directory.")
    for d in docs:
        print("-", d["id"])
