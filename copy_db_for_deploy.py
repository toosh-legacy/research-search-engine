#!/usr/bin/env python3
"""Copy database to api directory for Vercel deployment."""
import shutil
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent
DB_SOURCE = REPO_ROOT / "papers.db"
DB_DEST = REPO_ROOT / "api" / "papers.db"

if DB_SOURCE.exists():
    print(f"Copying {DB_SOURCE} to {DB_DEST}...")
    shutil.copy(DB_SOURCE, DB_DEST)
    print("✓ Database copied successfully")
    
    # Remove bm25.pkl if exists (will be rebuilt)
    bm25_path = REPO_ROOT / "api" / "bm25.pkl"
    if bm25_path.exists():
        bm25_path.unlink()
        print("✓ Removed old BM25 index (will rebuild on deployment)")
else:
    print(f"ERROR: {DB_SOURCE} not found!")
    print("Run scripts/00_seed_sqlite.py first to create the database")
    exit(1)
