#!/usr/bin/env python3
"""Export ALL papers from database to JSON for Vercel deployment."""
import sqlite3
import json
import gzip
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DB_SOURCE = REPO_ROOT / "papers.db"
JSON_DEST = REPO_ROOT / "api" / "papers_data.json"
JSON_COMPRESSED = REPO_ROOT / "api" / "papers_data.json.gz"

if not DB_SOURCE.exists():
    print(f"ERROR: {DB_SOURCE} not found!")
    exit(1)

print("Exporting ALL papers from database to JSON...")

conn = sqlite3.connect(DB_SOURCE)
c = conn.cursor()

# Get total count
total = c.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
print(f"Found {total} papers in database")

# Export all papers with all fields
papers = []
rows = c.execute("""
    SELECT paper_id, title, authors, abstract, published, updated, 
           categories, primary_category, url, pdf_url
    FROM papers 
    ORDER BY paper_id
""").fetchall()

print(f"Processing {len(rows)} papers...")
for i, row in enumerate(rows):
    if (i + 1) % 10000 == 0:
        print(f"  Processed {i + 1}/{len(rows)} papers...")
    
    papers.append({
        "id": row[0],
        "paper_id": row[0],  # Include both for compatibility
        "title": row[1] or "",
        "authors": row[2] or "",
        "abstract": row[3] or "",
        "published": row[4] or "",
        "updated": row[5] or "",
        "categories": row[6] or "",
        "category": row[7] or "",
        "primary_category": row[7] or "",
        "url": row[8] or "",
        "pdf_url": row[9] or ""
    })

conn.close()

# Write uncompressed JSON (for local use)
print(f"Writing to {JSON_DEST}...")
with open(JSON_DEST, 'w', encoding='utf-8') as f:
    json.dump(papers, f, ensure_ascii=False, separators=(',', ':'))  # Compact format

file_size_mb = JSON_DEST.stat().st_size / (1024 * 1024)
print(f"Exported {len(papers)} papers to {JSON_DEST}")
print(f"Uncompressed file size: {file_size_mb:.2f} MB")

# Also create compressed version for upload
print(f"Creating compressed version...")
with open(JSON_DEST, 'rb') as f_in:
    with gzip.open(JSON_COMPRESSED, 'wb') as f_out:
        f_out.writelines(f_in)

compressed_size_mb = JSON_COMPRESSED.stat().st_size / (1024 * 1024)
print(f"Compressed file size: {compressed_size_mb:.2f} MB")
print(f"Compression ratio: {compressed_size_mb/file_size_mb:.2%}")
print(f"\nNext steps:")
print(f"1. Upload {JSON_COMPRESSED.name} to external storage (S3, GitHub Releases, etc.)")
print(f"2. Set PAPERS_DATA_URL environment variable in Vercel to the download URL")
print(f"3. The API will automatically download and decompress it on first load")
