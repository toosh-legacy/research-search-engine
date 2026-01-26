import pickle
import sqlite3
from pathlib import Path
from rank_bm25 import BM25Okapi
import re

def tokenize(text: str) -> list[str]:
    """Enhanced tokenization for academic text."""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters but keep spaces and hyphens
    text = re.sub(r'[^\w\s-]', ' ', text)
    # Split on whitespace and filter out short tokens
    tokens = [t for t in text.split() if len(t) > 2]
    return tokens

def main() -> None:
    conn = sqlite3.connect("papers.db")
    cur = conn.cursor()
    cur.execute("SELECT paper_id, title, abstract FROM papers")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        raise RuntimeError("No rows found in papers.db. Run scripts/00_seed_sqlite.py first.")

    doc_ids: list[str] = []
    corpus: list[list[str]] = []

    for pid, title, abstract in rows:
        doc_ids.append(pid)
        corpus.append(tokenize(f"{title} {abstract}"))

    bm25 = BM25Okapi(corpus)

    output_path = Path(__file__).resolve().parent.parent / "app" / "bm25.pkl"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        pickle.dump({"doc_ids": doc_ids, "bm25": bm25}, f)

    print(f"Built BM25 for {len(doc_ids)} documents -> {output_path}")

if __name__ == "__main__":
    main()
