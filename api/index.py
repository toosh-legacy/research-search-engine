from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import sys
import json
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
DATA_PATH = BASE_DIR / "papers_data.json"

# Load papers data
PAPERS = []
PAPERS_BY_ID = {}

if DATA_PATH.exists():
    print(f"Loading papers from {DATA_PATH}...")
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        PAPERS = json.load(f)
    PAPERS_BY_ID = {p['id']: p for p in PAPERS}
    print(f"✓ Loaded {len(PAPERS)} papers")
else:
    print("WARNING: papers_data.json not found")

def tokenize(text: str) -> list[str]:
    """Enhanced tokenization for academic text."""
    if not text:
        return []
    text = text.lower()
    text = re.sub(r'[^\w\s-]', ' ', text)
    tokens = [t for t in text.split() if len(t) > 2]
    return tokens

def build_bm25_index():
    """Build BM25 index from papers data."""
    from rank_bm25 import BM25Okapi
    
    corpus = []
    for paper in PAPERS:
        combined = f"{paper.get('title', '')} {paper.get('abstract', '')}"
        tokens = tokenize(combined)
        corpus.append(tokens)
    
    return BM25Okapi(corpus)

# Build BM25 index on startup
BM25 = build_bm25_index() if PAPERS else None

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
    if not PAPERS:
        return {"results": [], "count": 0, "query": q}
    
    expanded_q = expand_query(q) if semantic else q
    query_tokens = tokenize(expanded_q)
    
    # BM25 scoring
    if BM25 and query_tokens:
        scores = BM25.get_scores(query_tokens)
        scored = [(i, score) for i, score in enumerate(scores)]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Get top results
        results = []
        for idx, score in scored:
            if len(results) >= limit:
                break
            
            paper = PAPERS[idx]
            
            # Apply filters
            if category and paper.get('category') != category:
                continue
            
            if year_min or year_max:
                try:
                    year = int(paper.get('published', '')[:4])
                    if year_min and year < year_min:
                        continue
                    if year_max and year > year_max:
                        continue
                except (ValueError, IndexError):
                    continue
            
            if author and author.lower() not in paper.get('authors', '').lower():
                continue
            
            results.append(paper)
    else:
        # No query tokens, return first N papers
        results = PAPERS[:limit]
    
    return {
        "results": results,
        "count": len(results),
        "query": expanded_q if semantic else q
    }

@app.get("/api/stats")
async def stats():
    """Get database statistics."""
    if not PAPERS:
        return {"total_papers": 0, "categories": {}, "year_range": [0, 0]}
    
    # Count categories
    categories = {}
    years = []
    
    for paper in PAPERS:
        cat = paper.get('category')
        if cat:
            categories[cat] = categories.get(cat, 0) + 1
        
        try:
            year = int(paper.get('published', '')[:4])
            years.append(year)
        except (ValueError, IndexError):
            pass
    
    year_range = [min(years), max(years)] if years else [2000, 2024]
    
    return {
        "total_papers": len(PAPERS),
        "categories": categories,
        "year_range": year_range
    }

@app.get("/api/facets")
async def facets():
    """Get available filter options."""
    if not PAPERS:
        return {"categories": [], "year_range": [2000, 2024]}
    
    categories = set()
    years = []
    
    for paper in PAPERS:
        cat = paper.get('category')
        if cat:
            categories.add(cat)
        
        try:
            year = int(paper.get('published', '')[:4])
            years.append(year)
        except (ValueError, IndexError):
            pass
    
    year_range = [min(years), max(years)] if years else [2000, 2024]
    
    return {
        "categories": sorted(list(categories)),
        "year_range": year_range
    }

@app.get("/api/suggestions")
async def suggestions(q: str = Query(..., min_length=1)):
    """Get search suggestions."""
    return {"suggestions": get_search_suggestions(q)}

# Vercel serverless handler
handler = Mangum(app)
