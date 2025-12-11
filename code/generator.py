import re
from typing import List, Dict

def first_sentence(text: str) -> str:
    """
    Return the first sentence-like fragment from text.
    Handles Sanskrit danda '।' and common punctuation.
    """
    parts = re.split(r'(?<=[।\.\?\!])\s+', text.strip())
    return parts[0] if parts and parts[0] else text.strip()[:200]

def generate_answer(query: str, retrieved_chunks: List[Dict], k:int = 3) -> str:
    """
    Lightweight, CPU-friendly generator:
    - Extracts first sentence from each retrieved chunk
    - Concatenates them into a short synthesized answer
    - Lists sources
    This is intentionally simple for a demo/assignment.
    """
    if not retrieved_chunks:
        return "No relevant information found in corpus."

    key_sentences = [first_sentence(ch["text"]) for ch in retrieved_chunks[:k]]
    summary = " ".join(key_sentences).strip()
    if len(summary.split()) > 250:
        summary = " ".join(summary.split()[:250]) + "..."

    answer = []
    answer.append(f"Query: {query}\n")
    answer.append("Short synthesized answer (from corpus):")
    answer.append(summary + "\n")
    answer.append("Sources (top results):")
    for ch in retrieved_chunks[:k]:
        answer.append(f"- {ch['id']} (file: {ch.get('source','unknown')}, score: {ch.get('score',0):.3f})")
    return "\n".join(answer)

# Optional: if you later want to integrate a small local transformer model for better generation,
# add a function `generate_with_transformer(prompt, model_name, device="cpu")` that uses
# Hugging Face transformers. Keep it optional because it increases CPU time and dependencies.
#
# Example (commented):
#
# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch
#
# def generate_with_transformer(prompt: str, model_name: str = "gpt2", max_length: int = 200):
#     tok = AutoTokenizer.from_pretrained(model_name)
#     model = AutoModelForCausalLM.from_pretrained(model_name)
#     inputs = tok(prompt, return_tensors="pt")
#     out = model.generate(**inputs, max_length=max_length, do_sample=True, top_p=0.9)
#     return tok.decode(out[0], skip_special_tokens=True)

if __name__ == "__main__":
    sample_chunk = {"id":"chunk_0", "source":"demo.txt", "text":"यह एक परीक्षण अंश है। यह दूसरा वाक्य।"}
    print(generate_answer("क्या यह परीक्षण है?", [sample_chunk]))
