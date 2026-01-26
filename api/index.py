from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import sys
import sqlite3
import pickle
import re
from pathlib import Path
from typing import Optional

# Copy the query expansion code inline for Vercel
POPULAR_SEARCHES = [
    "machine learning", "neural networks", "deep learning", "quantum computing",
    "computer vision", "natural language processing", "reinforcement learning"
]

def expand_query(query: str) -> str:
    """Simple query expansion."""
    return query.lower().strip()

def get_search_suggestions(partial: str, limit: int = 5) -> list[str]:
    """Get search suggestions."""
    partial = partial.lower()
    suggestions = [s for s in POPULAR_SEARCHES if partial in s]
    return suggestions[:limit]

# Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "papers.db"
BM25_PATH = BASE_DIR / "bm25.pkl"

def tokenize(text: str) -> list[str]:
    """Enhanced tokenization for academic text."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', ' ', text)
    tokens = [t for t in text.split() if len(t) > 2]
    return tokens

def build_bm25_index():
    """Build BM25 index from database."""
    print("Building BM25 index from database...")
    from rank_bm25 import BM25Okapi
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    rows = c.execute("SELECT id, title, abstract FROM papers ORDER BY id").fetchall()
    conn.close()
    
    doc_ids = []
    corpus = []
    
    for paper_id, title, abstract in rows:
        doc_ids.append(paper_id)
        combined = f"{title or ''} {abstract or ''}"
        tokens = tokenize(combined)
        corpus.append(tokens)
    
    bm25 = BM25Okapi(corpus)
    
    with open(BM25_PATH, "wb") as f:
        pickle.dump({"doc_ids": doc_ids, "bm25": bm25}, f)
    
    print(f"✓ BM25 index built with {len(doc_ids)} papers")
    return doc_ids, bm25

# Load or build BM25 index
if DB_PATH.exists():
    if not BM25_PATH.exists():
        print("Building BM25 index...")
        DOC_IDS, BM25 = build_bm25_index()
    else:
        with open(BM25_PATH, "rb") as f:
            state = pickle.load(f)
        DOC_IDS = state["doc_ids"]
        BM25 = state["bm25"]
else:
    # Fallback for deployment - empty index
    DOC_IDS = []
    BM25 = None
    print("WARNING: papers.db not found. Search will not work.")

@app.get("/api/search")
async def search(
    q: str = Query(..., min_length=1),
    category: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    author: Optional[str] = None,
    sort_by: str = "relevance",
    semantic: bool = False,
    limit: int = Query(50, ge=1, le=100)
):
    """Search papers with filters."""
    if not DB_PATH.exists():
        return {"results": [], "count": 0, "query": q}
    
    expanded_q = expand_query(q) if semantic else q
    query_tokens = tokenize(expanded_q)
    
    # BM25 scoring
    if BM25 and query_tokens:
        scores = BM25.get_scores(query_tokens)
        scored = [(doc_id, score) for doc_id, score in zip(DOC_IDS, scores)]
        scored.sort(key=lambda x: x[1], reverse=True)
        top_ids = [doc_id for doc_id, _ in scored[:limit * 2]]
    else:
        top_ids = DOC_IDS[:limit * 2]
    
    # Build SQL query with filters
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    sql = "SELECT id, title, authors, abstract, published, pdf_url, arxiv_id, category FROM papers WHERE id IN ({})".format(
        ','.join('?' * len(top_ids))
    )
    
    filters = []
    params = list(top_ids)
    
    if category:
        filters.append("category = ?")
        params.append(category)
    if year_min:
        filters.append("CAST(substr(published, 1, 4) AS INTEGER) >= ?")
        params.append(year_min)
    if year_max:
        filters.append("CAST(substr(published, 1, 4) AS INTEGER) <= ?")
        params.append(year_max)
    if author:
        filters.append("authors LIKE ?")
        params.append(f"%{author}%")
    
    if filters:
        sql += " AND " + " AND ".join(filters)
    
    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()
    
    # Re-sort by BM25 score
    id_to_row = {row[0]: row for row in rows}
    results = []
    
    for doc_id in top_ids:
        if doc_id in id_to_row:
            row = id_to_row[doc_id]
            results.append({
                "id": row[0],
                "title": row[1],
                "authors": row[2],
                "abstract": row[3],
                "published": row[4],
                "pdf_url": row[5],
                "arxiv_id": row[6],
                "category": row[7]
            })
            if len(results) >= limit:
                break
    
    return {
        "results": results,
        "count": len(results),
        "query": expanded_q if semantic else q
    }

@app.get("/api/stats")
async def stats():
    """Get database statistics."""
    if not DB_PATH.exists():
        return {"total_papers": 0, "categories": {}, "year_range": [0, 0]}
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    total = c.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    
    cat_counts = c.execute(
        "SELECT category, COUNT(*) FROM papers GROUP BY category ORDER BY COUNT(*) DESC"
    ).fetchall()
    
    years = c.execute(
        "SELECT MIN(CAST(substr(published, 1, 4) AS INTEGER)), MAX(CAST(substr(published, 1, 4) AS INTEGER)) FROM papers"
    ).fetchone()
    
    conn.close()
    
    return {
        "total_papers": total,
        "categories": {cat: count for cat, count in cat_counts},
        "year_range": list(years)
    }

@app.get("/api/facets")
async def facets():
    """Get available filter options."""
    if not DB_PATH.exists():
        return {"categories": [], "year_range": [2000, 2024]}
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    cats = c.execute("SELECT DISTINCT category FROM papers ORDER BY category").fetchall()
    years = c.execute(
        "SELECT MIN(CAST(substr(published, 1, 4) AS INTEGER)), MAX(CAST(substr(published, 1, 4) AS INTEGER)) FROM papers"
    ).fetchone()
    
    conn.close()
    
    return {
        "categories": [c[0] for c in cats if c[0]],
        "year_range": list(years) if years[0] else [2000, 2024]
    }

@app.get("/api/suggestions")
async def suggestions(q: str = Query(..., min_length=1)):
    """Get search suggestions."""
    return {"suggestions": get_search_suggestions(q)}

# Vercel serverless handler
handler = Mangum(app)
