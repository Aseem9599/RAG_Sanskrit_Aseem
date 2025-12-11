import os
import json
import pickle
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

INDEX_PATH = "../data/index.pkl"

class TFIDFRetriever:
    def __init__(self, max_features: int = 20000):
        self.vectorizer = None
        self.matrix = None
        self.ids = []
        self.sources = []
        self.texts = []
        self.max_features = max_features

    def fit(self, chunks: List[Dict]):
        """
        chunks: list of {"id":..., "source":..., "text":...}
        """
        self.ids = [c["id"] for c in chunks]
        self.sources = [c.get("source", "unknown") for c in chunks]
        self.texts = [c["text"] for c in chunks]
        self.vectorizer = TfidfVectorizer(max_features=self.max_features)
        self.matrix = self.vectorizer.fit_transform(self.texts)

    def save(self, path: str = INDEX_PATH):
        path = os.path.abspath(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({
                "vectorizer": self.vectorizer,
                "matrix": self.matrix,
                "ids": self.ids,
                "sources": self.sources,
                "texts": self.texts
            }, f)

    def load(self, path: str = INDEX_PATH):
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Index not found at {path}")
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.vectorizer = data["vectorizer"]
        self.matrix = data["matrix"]
        self.ids = data["ids"]
        self.sources = data["sources"]
        self.texts = data["texts"]

    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        """
        Return top-k chunks for the query with scores.
        Each result: {"id":..., "source":..., "text":..., "score":...}
        """
        if self.vectorizer is None or self.matrix is None:
            raise RuntimeError("Retriever not fitted or loaded.")
        qv = self.vectorizer.transform([query])
        sims = cosine_similarity(qv, self.matrix)[0]
        top_idx = sims.argsort()[::-1][:k]
        results = []
        for i in top_idx:
            results.append({
                "id": self.ids[i],
                "source": self.sources[i],
                "text": self.texts[i],
                "score": float(sims[i])
            })
        return results

# Utility to build index from chunks.jsonl
def build_index_from_chunks(chunks_path: str = "../data/chunks.jsonl", index_out: str = INDEX_PATH):
    if not os.path.exists(chunks_path):
        raise FileNotFoundError(f"Chunks file not found: {chunks_path}")
    chunks = []
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            chunks.append(obj)
    retriever = TFIDFRetriever()
    retriever.fit(chunks)
    retriever.save(index_out)
    print(f"Built TF-IDF index with {len(chunks)} chunks and saved to {index_out}")

if __name__ == "__main__":
    base = os.path.dirname(__file__)
    chunks_file = os.path.join(base, "..", "data", "chunks.jsonl")
    build_index_from_chunks(chunks_path=chunks_file, index_out=os.path.join(base, "..", "data", "index.pkl"))
