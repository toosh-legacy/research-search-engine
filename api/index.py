from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sys
import json
import re
from pathlib import Path
from typing import Optional
import pickle
import os
import urllib.request

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
REPO_ROOT = BASE_DIR.parent
DATA_PATH = BASE_DIR / "papers_data.json"

# Load papers data (normalize fields so both db-export and original JSON work)
PAPERS = []
PAPERS_BY_ID = {}

if DATA_PATH.exists():
    print(f"Loading papers from {DATA_PATH}...")
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    for item in raw:
        pid = item.get('paper_id') or item.get('id') or item.get('paperId')
        categories = item.get('categories') or item.get('category') or ''
        # normalize primary category
        primary = item.get('primary_category')
        if not primary and categories:
            # categories may be comma or space separated
            cats = [c.strip() for c in re.split(r"[\s,]+", categories) if c.strip()]
            primary = cats[0] if cats else ''

        paper = {
            'id': pid,
            'title': item.get('title', ''),
            'abstract': item.get('abstract', ''),
            'authors': item.get('authors', ''),
            'categories': categories,
            'category': primary,
            'published': item.get('published', ''),
            'updated': item.get('updated', ''),
            'url': item.get('url') or item.get('html_url') or item.get('link'),
            'pdf_url': item.get('pdf_url') or item.get('pdf') or ''
        }
        PAPERS.append(paper)

    PAPERS_BY_ID = {p['id']: p for p in PAPERS if p.get('id')}
    print(f"Loaded {len(PAPERS)} papers")
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

# Try to load a prebuilt BM25 index to avoid rebuilding on cold start.
BM25 = None
DOC_IDS = None
BM25_PKL = REPO_ROOT / 'app' / 'bm25.pkl'
if BM25_PKL.exists():
    try:
        with open(BM25_PKL, 'rb') as f:
            data = pickle.load(f)
        DOC_IDS = data.get('doc_ids')
        BM25 = data.get('bm25')
        print(f"Loaded BM25 index from {BM25_PKL} (docs: {len(DOC_IDS)})")
    except Exception as e:
        print(f"Failed to load BM25 pickle: {e}")
        BM25 = None
        DOC_IDS = None
else:
    # Try to download BM25 from a URL if provided in environment (useful for Vercel)
    BM25_URL = os.environ.get('BM25_URL')
    if BM25_URL:
        try:
            print(f"Downloading BM25 from {BM25_URL}...")
            BM25_PKL.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(BM25_URL, BM25_PKL)
            with open(BM25_PKL, 'rb') as f:
                data = pickle.load(f)
            DOC_IDS = data.get('doc_ids')
            BM25 = data.get('bm25')
            print(f"Downloaded and loaded BM25 (docs: {len(DOC_IDS)})")
        except Exception as e:
            print(f"Failed to download BM25: {e}")
            BM25 = None
            DOC_IDS = None
    else:
        print("No prebuilt BM25 found; BM25 will be built lazily if needed")

@app.get("/api/search")
@app.get("/search")
async def search(
    q: str = Query(..., min_length=1),
    category: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    author: Optional[str] = None,
    sort_by: str = "relevance",
    semantic: str = "false",
    limit: int = Query(50, ge=1, le=100)
):
    """Search papers with filters."""
    if not PAPERS:
        return {"results": [], "count": 0, "query": q, "error": "No papers loaded"}
    
    # Convert semantic string to boolean
    use_semantic = semantic.lower() in ("true", "1", "yes")
    expanded_q = expand_query(q) if use_semantic else q
    query_tokens = tokenize(expanded_q)
    
    # BM25 scoring (use prebuilt DOC_IDS mapping if available)
    if BM25 and query_tokens:
        scores = BM25.get_scores(query_tokens)
        scored = [(i, score) for i, score in enumerate(scores)]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Get top results
        results = []
        for idx, score in scored:
            if len(results) >= limit:
                break

            # Map BM25 index -> paper id -> paper object
            if DOC_IDS:
                pid = DOC_IDS[idx]
                paper = PAPERS_BY_ID.get(pid)
            else:
                # fallback: assume PAPERS order matches BM25
                paper = PAPERS[idx] if idx < len(PAPERS) else None

            if not paper:
                continue

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
@app.get("/stats")
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
@app.get("/facets")
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
@app.get("/suggestions")
async def suggestions(q: str = Query(..., min_length=1)):
    """Get search suggestions."""
    return {"suggestions": get_search_suggestions(q)}

@app.get("/api/health")
@app.get("/health")
@app.get("/")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "papers_loaded": len(PAPERS),
        "bm25_loaded": BM25 is not None,
        "data_path": str(DATA_PATH),
        "data_exists": DATA_PATH.exists()
    }

# For Vercel Python runtime, FastAPI app is automatically detected
# Routes are defined without /api prefix since Vercel routes /api/* to this file
