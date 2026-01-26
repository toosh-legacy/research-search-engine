#!/usr/bin/env python3
"""Export a subset of papers to JSON for Vercel deployment."""
import sqlite3
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DB_SOURCE = REPO_ROOT / "papers.db"
JSON_DEST = REPO_ROOT / "api" / "papers_data.json"

# Export 2000 papers (representative sample)
SAMPLE_SIZE = 2000

if not DB_SOURCE.exists():
    print(f"ERROR: {DB_SOURCE} not found!")
    exit(1)

print(f"Exporting {SAMPLE_SIZE} papers to JSON...")

conn = sqlite3.connect(DB_SOURCE)
c = conn.cursor()

# Get a diverse sample across categories
papers = []
rows = c.execute("""
    SELECT paper_id, title, authors, abstract, published, pdf_url, primary_category 
    FROM papers 
    ORDER BY RANDOM() 
    LIMIT ?
""", (SAMPLE_SIZE,)).fetchall()

for row in rows:
    papers.append({
        "id": row[0],
        "title": row[1],
        "authors": row[2],
        "abstract": row[3],
        "published": row[4],
        "pdf_url": row[5],
        "category": row[6]
    })

conn.close()

# Write to JSON
with open(JSON_DEST, 'w', encoding='utf-8') as f:
    json.dump(papers, f, indent=2)

file_size_mb = JSON_DEST.stat().st_size / (1024 * 1024)
print(f"Exported {len(papers)} papers to {JSON_DEST}")
print(f"File size: {file_size_mb:.2f} MB")
print(f"Ready for Vercel deployment!")
