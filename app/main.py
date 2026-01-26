import pickle
import sqlite3
import re
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Import query expansion functions
import sys
sys.path.insert(0, str(Path(__file__).parent))
from query_expansion import expand_query, get_search_suggestions, POPULAR_SEARCHES


app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",
        "https://*.vercel.app",  # Vercel deployments
        "*"  # Allow all origins in production (or restrict to your domain)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def tokenize(text: str) -> list[str]:
    """Enhanced tokenization for academic text."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', ' ', text)
    tokens = [t for t in text.split() if len(t) > 2]
    return tokens

@app.get("/")
def root():
    return {
        "status": "ok",
        "endpoints": {
            "docs": "/docs",
            "search": "/search?q=transformer&category=cs.LG&year=2017",
            "stats": "/stats",
            "ui": "/ui"
        }
    }

def fetch_papers_by_ids(ids: list[str]) -> list[dict]:
    if not ids:
        return []

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    qmarks = ",".join(["?"] * len(ids))
    cur.execute(
        f"""
        SELECT paper_id, title, authors, categories, primary_category, published, url, pdf_url, abstract
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
            "primary_category": r[4],
            "published": r[5],
            "url": r[6],
            "pdf_url": r[7],
            "abstract": r[8],
        }
        for r in rows
    }
    return [by_id[i] for i in ids if i in by_id]

@app.get("/stats")
def get_stats():
    """Get database statistics with detailed breakdowns."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    total_papers = cur.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    
    # Get primary category distribution (not all categories)
    cur.execute("""
        SELECT primary_category, COUNT(*) as count 
        FROM papers 
        WHERE primary_category IS NOT NULL AND primary_category != ''
        GROUP BY primary_category 
        ORDER BY count DESC 
        LIMIT 20
    """)
    category_counts = dict(cur.fetchall())
    
    # Get year distribution
    cur.execute("""
        SELECT substr(published, 1, 4) as year, COUNT(*) 
        FROM papers 
        WHERE published IS NOT NULL
        GROUP BY year 
        ORDER BY year DESC
        LIMIT 10
    """)
    year_counts = dict(cur.fetchall())
    
    # Get recent papers count
    cur.execute("""
        SELECT COUNT(*) FROM papers 
        WHERE published >= date('now', '-1 year')
    """)
    recent_count = cur.fetchone()[0]
    
    conn.close()
    
    return {
        "total_papers": total_papers,
        "recent_papers_1yr": recent_count,
        "top_categories": category_counts,
        "papers_by_year": year_counts,
    }

@app.get("/facets")
def get_facets(q: Optional[str] = None):
    """Get facet counts for filtering (optionally filtered by query)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Get all primary categories with counts
    cur.execute("""
        SELECT primary_category, COUNT(*) as count 
        FROM papers 
        WHERE primary_category IS NOT NULL AND primary_category != ''
        GROUP BY primary_category 
        ORDER BY count DESC
    """)
    categories = [{"value": row[0], "count": row[1]} for row in cur.fetchall()]
    
    # Get year range
    cur.execute("""
        SELECT MIN(substr(published, 1, 4)), MAX(substr(published, 1, 4))
        FROM papers
        WHERE published IS NOT NULL
    """)
    year_range = cur.fetchone()
    
    conn.close()
    
    return {
        "categories": categories,
        "year_range": {"min": year_range[0], "max": year_range[1]} if year_range else None,
    }

@app.get("/search")
def search(
    q: str,
    k: int = Query(default=10, ge=1, le=100),
    category: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    year: Optional[int] = None,  # Kept for backwards compatibility
    author: Optional[str] = None,
    sort: str = Query(default="relevance", pattern="^(relevance|date_desc|date_asc)$"),
    semantic: bool = Query(default=True, description="Enable semantic query expansion"),
):
    """Search papers with advanced filters and semantic understanding.
    
    Filters:
    - category: Primary category (e.g., cs.LG, cs.AI)
    - year: Specific year (backwards compatible)
    - year_from/year_to: Date range
    - author: Author name (substring match)
    - sort: relevance (default), date_desc, date_asc
    - semantic: Enable query expansion for casual/natural language (default: True)
    """
    q = q.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter q cannot be empty.")

    # Apply semantic query expansion
    expanded_queries = [q]
    if semantic:
        expanded_queries = expand_query(q)
    
    # Tokenize all expanded queries
    all_tokens = []
    for query in expanded_queries:
        all_tokens.extend(tokenize(query))
    
    # Remove duplicates while preserving order
    seen = set()
    tokens = []
    for t in all_tokens:
        if t not in seen:
            seen.add(t)
            tokens.append(t)
    
    scores = BM25.get_scores(tokens)

    # Get top candidates (fetch more to allow for filtering)
    ranked = sorted(zip(DOC_IDS, scores), key=lambda x: x[1], reverse=True)[:k * 10]
    candidate_ids = [pid for pid, _ in ranked]
    score_map = dict(ranked)

    # Fetch papers and apply filters
    papers = fetch_papers_by_ids(candidate_ids)
    
    filtered_papers = []
    for paper in papers:
        # Apply primary category filter (exact match)
        if category and paper.get("primary_category") != category:
            continue
        
        # Apply year filter (backwards compatible)
        if year and not paper["published"].startswith(str(year)):
            continue
        
        # Apply year range filter
        paper_year = int(paper["published"][:4]) if paper["published"] else 0
        if year_from and paper_year < year_from:
            continue
        if year_to and paper_year > year_to:
            continue
        
        # Apply author filter (case-insensitive substring match)
        if author and author.lower() not in paper["authors"].lower():
            continue
        
        # Add relevance score
        paper["score"] = score_map.get(paper["paper_id"], 0.0)
        filtered_papers.append(paper)
    
    # Sort results
    if sort == "date_desc":
        filtered_papers.sort(key=lambda x: x["published"], reverse=True)
    elif sort == "date_asc":
        filtered_papers.sort(key=lambda x: x["published"])
    # relevance is already sorted by BM25 score
    
    # Limit to requested number
    filtered_papers = filtered_papers[:k]
    
    return {
        "query": q,
        "expanded_terms": expanded_queries if semantic else [q],
        "filters": {
            "category": category,
            "year": year,
            "year_from": year_from,
            "year_to": year_to,
            "author": author,
            "sort": sort,
            "semantic": semantic,
        },
        "total_results": len(filtered_papers),
        "results": filtered_papers
    }

@app.get("/suggestions")
def get_suggestions(q: str = Query(default="", description="Partial query for autocomplete")):
    """Get search suggestions for autocomplete."""
    if len(q) < 2:
        return {"suggestions": POPULAR_SEARCHES[:10]}
    
    suggestions = get_search_suggestions(q)
    
    # Also search for matching paper titles (if query is long enough)
    if len(q) >= 3:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT title 
            FROM papers 
            WHERE title LIKE ? 
            LIMIT 5
        """, (f"%{q}%",))
        title_suggestions = [row[0] for row in cur.fetchall()]
        conn.close()
        suggestions.extend(title_suggestions)
    
    return {"query": q, "suggestions": suggestions[:10]}
