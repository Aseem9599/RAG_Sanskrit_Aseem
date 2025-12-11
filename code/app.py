import os
import argparse
import json

# TF-IDF retriever
from retriever import TFIDFRetriever, build_index_from_chunks

# Embedding retriever
from retriever_emb import EmbeddingRetriever

# Generator
from generator import generate_answer

BASE = os.path.join(os.path.dirname(__file__), "..")
CHUNKS_FILE = os.path.join(BASE, "data", "chunks.jsonl")
INDEX_FILE = os.path.join(BASE, "data", "index.pkl")

def load_chunks():
    chunks = []
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks

def ensure_tfidf_index():
    if not os.path.exists(INDEX_FILE):
        print("Index not found. Building TF-IDF index...")
        build_index_from_chunks(chunks_path=CHUNKS_FILE, index_out=INDEX_FILE)

    r = TFIDFRetriever()
    r.load(INDEX_FILE)
    return r

def main():
    parser = argparse.ArgumentParser(description="RAG System (TF-IDF or Embedding based)")
    parser.add_argument("--query", "-q", type=str, help="Your query")
    parser.add_argument("--k", type=int, default=3, help="Number of chunks to retrieve")
    parser.add_argument("--use-emb", action="store_true", help="Use embedding-based retriever")
    args = parser.parse_args()

    if not args.query:
        args.query = input("Enter query: ").strip()

    if args.use_emb:
        print("\nUsing Sentence-Transformer Embedding Retriever...\n")
        r = EmbeddingRetriever()
        results = r.retrieve(args.query, k=args.k)

    else:
        print("\nUsing TF-IDF Retriever...\n")
        r = ensure_tfidf_index()
        results = r.retrieve(args.query, k=args.k)

    # Display retrieved chunks
    print("Top Retrieved Chunks:")
    for i, rch in enumerate(results, 1):
        print(f"{i}. {rch['id']} ({rch['source']}) score={rch['score']:.4f}")
        print("   ", rch["text"][:200].replace("\n", " "), "...\n")

    # Generate final answer
    answer = generate_answer(args.query, results, k=args.k)
    print("=" * 60)
    print(answer)
    print("=" * 60)

if __name__ == "__main__":
    main()
