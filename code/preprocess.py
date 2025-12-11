import os
import json
import re
from typing import List

# Adjustable parameters
MAX_WORDS_PER_CHUNK = 200       # ~200 words per chunk
OVERLAP_WORDS = 40              # overlap between consecutive chunks
OUTPUT_CHUNKS_FILE = "../data/chunks.jsonl"

def simple_sentence_split(text: str) -> List[str]:
    """
    Split text into 'sentences' using common sentence-ending punctuation.
    Works for Sanskrit when sentences use '।' as well as for English punctuation.
    """
    # Normalize whitespace
    text = text.replace("\r\n", " ").replace("\n", " ").strip()
    # Keep Sanskrit danda '।' as sentence terminator with spaces after split
    sents = re.split(r'(?<=[।\.\?\!])\s+', text)
    sents = [s.strip() for s in sents if s.strip()]
    return sents

def chunk_text(text: str, max_words: int = MAX_WORDS_PER_CHUNK, overlap: int = OVERLAP_WORDS) -> List[str]:
    """
    Create chunks of approx max_words words, with 'overlap' words overlapping between chunks.
    Returns list of chunk strings.
    """
    sents = simple_sentence_split(text)
    chunks = []
    cur_words = 0
    cur_tokens = []

    for sent in sents:
        words = sent.split()
        if cur_words + len(words) > max_words and cur_tokens:
            chunks.append(" ".join(cur_tokens).strip())
            # create overlap
            all_words = " ".join(cur_tokens).split()
            overlap_words = all_words[-overlap:] if len(all_words) > overlap else all_words
            cur_tokens = overlap_words + words
            cur_words = len(cur_tokens)
        else:
            cur_tokens.extend(words)
            cur_words += len(words)

    if cur_tokens:
        chunks.append(" ".join(cur_tokens).strip())

    return chunks

def create_chunks_from_data(data_dir: str = "../data", out_path: str = OUTPUT_CHUNKS_FILE,
                            max_words: int = MAX_WORDS_PER_CHUNK, overlap: int = OVERLAP_WORDS) -> int:
    """
    Read all .txt files from data_dir, chunk them, and write chunks as JSONL to out_path.
    Each line: {"id": "chunk_0", "source": "<filename>", "text": "<chunk text>"}
    Returns number of chunks written.
    """
    data_dir = os.path.abspath(data_dir)
    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    chunk_id = 0
    with open(out_path, "w", encoding="utf-8") as outf:
        for fname in sorted(os.listdir(data_dir)):
            if not fname.lower().endswith(".txt"):
                continue
            fpath = os.path.join(data_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                text = f.read()
            if not text.strip():
                continue
            chunks = chunk_text(text, max_words=max_words, overlap=overlap)
            for ch in chunks:
                rec = {"id": f"chunk_{chunk_id}", "source": fname, "text": ch}
                outf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                chunk_id += 1

    return chunk_id

if __name__ == "__main__":
    base = os.path.dirname(__file__)
    n = create_chunks_from_data(data_dir=os.path.join(base, "..", "data"),
                                out_path=os.path.join(base, "..", "data", "chunks.jsonl"))
    print(f"Wrote {n} chunks to ../data/chunks.jsonl")
