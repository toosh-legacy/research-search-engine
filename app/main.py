import pickle
import sqlite3
from pathlib import Path
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Robust paths (works no matter where you launch uvicorn from)
APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parent

BM25_PATH = APP_DIR / "bm25.pkl"
DB_PATH = REPO_ROOT / "papers.db"

if not BM25_PATH.exists():
    raise RuntimeError(
        f"Missing BM25 index: {BM25_PATH}. Build it with: uv run python scripts/01_build_bm25.py"
    )

if not DB_PATH.exists():
    raise RuntimeError(
        f"Missing database: {DB_PATH}. Create it with: uv run python scripts/00_seed_sqlite.py"
    )

with open(BM25_PATH, "rb") as f:
    state = pickle.load(f)

DOC_IDS = state["doc_ids"]
BM25 = state["bm25"]

@app.get("/")
def root():
    return {
        "status": "ok",
        "docs": "/docs",
        "try": "/search?q=transformer"
    }

def fetch_papers_by_ids(ids: list[str]) -> list[dict]:
    if not ids:
        return []

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    qmarks = ",".join(["?"] * len(ids))
    cur.execute(
        f"""
        SELECT paper_id, title, authors, categories, published, url, pdf_url, abstract
        FROM papers
        WHERE paper_id IN ({qmarks})
        """,
        ids,
    )
    rows = cur.fetchall()
    conn.close()

    # map results for stable ordering
    by_id = {
        r[0]: {
            "paper_id": r[0],
            "title": r[1],
            "authors": r[2],
            "categories": r[3],
            "published": r[4],
            "url": r[5],
            "pdf_url": r[6],
            "abstract": r[7],
        }
        for r in rows
    }
    return [by_id[i] for i in ids if i in by_id]

@app.get("/search")
def search(q: str, k: int = 10):
    q = q.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter q cannot be empty.")

    tokens = q.lower().split()
    scores = BM25.get_scores(tokens)

    ranked = sorted(zip(DOC_IDS, scores), key=lambda x: x[1], reverse=True)[:k]
    top_ids = [pid for pid, _ in ranked]

    results = fetch_papers_by_ids(top_ids)
    return {"query": q, "results": results}
