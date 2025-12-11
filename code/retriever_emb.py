# code/retriever_emb.py
import os, pickle
import numpy as np
from sentence_transformers import SentenceTransformer

BASE = os.path.join(os.path.dirname(__file__), "..")
EMB_PATH = os.path.join(BASE, "data", "embeddings.npy")
META_PATH = os.path.join(BASE, "data", "emb_meta.pkl")
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

class EmbeddingRetriever:
    def __init__(self, model_name=MODEL_NAME):
        if not os.path.exists(EMB_PATH) or not os.path.exists(META_PATH):
            raise FileNotFoundError("Embeddings not found. Run code/build_embeddings.py first.")
        self.emb = np.load(EMB_PATH)
        with open(META_PATH, "rb") as f:
            meta = pickle.load(f)
        self.ids = meta["ids"]
        self.sources = meta["sources"]
        self.model = SentenceTransformer(model_name)
        # ensure embeddings normalized
        norms = np.linalg.norm(self.emb, axis=1, keepdims=True)
        norms[norms==0] = 1.0
        self.emb = self.emb / norms

    def retrieve(self, query, k=3):
        q_emb = self.model.encode([query], convert_to_numpy=True)
        q_emb = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True)+1e-10)
        sims = (self.emb @ q_emb[0]).astype(float)  # cosine since normalized
        top_idx = np.argsort(sims)[::-1][:k]
        results = []
        from json import loads
        chunks_file = os.path.join(BASE, "data", "chunks.jsonl")
        all_chunks = {}
        with open(chunks_file, "r", encoding="utf-8") as f:
            for line in f:
                obj = loads(line)
                all_chunks[obj["id"]] = obj
        for i in top_idx:
            cid = self.ids[i]
            rec = all_chunks.get(cid, {"id":cid, "text":"", "source": self.sources[i]})
            results.append({"id": cid, "text": rec.get("text",""), "source": rec.get("source","unknown"), "score": float(sims[i])})
        return results
