# code/build_embeddings.py
import os, json, pickle
import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "chunks.jsonl")
EMB_OUT = os.path.join(os.path.dirname(__file__), "..", "data", "embeddings.npy")
META_OUT = os.path.join(os.path.dirname(__file__), "..", "data", "emb_meta.pkl")
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"


def load_chunks(path=CHUNKS_FILE):
    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks

def build_and_save():
    chunks = load_chunks()
    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    sources = [c.get("source","unknown") for c in chunks]

    print("Loading model:", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)
    print(f"Encoding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    # normalize embeddings for cosine via dot product
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms==0] = 1.0
    embeddings = embeddings / norms

    np.save(EMB_OUT, embeddings)
    with open(META_OUT, "wb") as f:
        pickle.dump({"ids": ids, "sources": sources}, f)
    print("Saved embeddings to", EMB_OUT)
    print("Saved metadata to", META_OUT)

if __name__ == "__main__":
    build_and_save()
