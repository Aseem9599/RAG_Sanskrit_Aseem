from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys

# Ensure code package path
BASE = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(os.path.abspath(os.path.join(BASE, "code")))

# Import retriever + generator (make sure names match your files)
from retriever_emb import EmbeddingRetriever
from generator import generate_answer

app = Flask(__name__)
CORS(app)

# Initialize retriever once (loads embeddings and model)
retriever = EmbeddingRetriever()

@app.route("/query", methods=["POST"])
def query_api():
    data = request.get_json(force=True)
    query = data.get("query", "").strip()
    k = int(data.get("k", 3))
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    results = retriever.retrieve(query, k=k)
    answer = generate_answer(query, results, k=k)
    return jsonify({"answer": answer, "chunks": results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
