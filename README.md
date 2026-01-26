# Research Paper Search Engine

A full-featured search engine for academic research papers from arXiv, with **semantic understanding** and natural language queries.

## ✨ Features

- 🧠 **Semantic Search** - Use casual language like "ai chatbot" or "machine learning for pictures"
- 🔍 **Full-text BM25 Ranking** - Fast and relevant results
- 🎯 **Advanced Filtering** - Filter by category, year, author, and sort options
- 💬 **Search Suggestions** - Intelligent autocomplete as you type
- 📊 **Statistics Dashboard** - Overview of your paper collection
- 🌍 **Diverse Research Areas** - Papers from CS, Math, Physics, Biology, Economics
- 🎨 **Modern Web UI** - Clean, responsive interface
- 🚀 **arXiv Integration** - Fetch real papers from 28+ categories
- ⚡ **Fast & Free** - No external APIs or costs

## 🎉 What's New: Semantic Search

Search like you talk! The engine now understands everyday language:

- "machine learning for pictures" → finds computer vision papers
- "ai chatbot" → finds dialogue systems, LLMs, GPT papers  
- "self driving cars" → finds autonomous vehicle research
- "robot learning" → finds robotics and RL papers

**See [SEMANTIC_SEARCH.md](SEMANTIC_SEARCH.md) for details**

## Quick Start

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync
```

### 2. Fetch Papers from arXiv

**Quick start (100 papers):**
```bash
uv run python scripts/fetch_arxiv.py --query "cat:cs.LG OR cat:cs.AI" --max-results 100
```

**Get as many papers as possible (recommended):**
```bash
# Fetch 50,000 papers across all fields (~15 hours)
uv run python scripts/fetch_all_arxiv.py --target 50000 --per-category-year 500 --start-year 2018

# Or go for maximum (~80k papers, ~24 hours)
uv run python scripts/fetch_all_arxiv.py --target 80000 --per-category-year 800 --start-year 2015
```

**See [FETCH_ALL.md](FETCH_ALL.md) for complete guide on fetching maximum papers**

### 3. Build the Search Index

```bash
uv run python scripts/01_build_bm25.py
```

### 4. Start the Server

```bash
uv run uvicorn app.main:app --reload
```

### 5. Open the Web UI

Visit: http://localhost:8000/ui

## API Endpoints

- `GET /ui` - Web interface
- `GET /search` - Search papers (with filters)
- `GET /stats` - Database statistics
- `GET /docs` - Interactive API documentation

## Technologies Used

- **FastAPI** - Modern web framework
- **BM25 (rank-bm25)** - Information retrieval algorithm
- **SQLite** - Lightweight database
- **arXiv API** - Paper data source
