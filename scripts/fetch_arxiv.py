"""
Fetch research papers from arXiv API.
Usage: uv run python scripts/fetch_arxiv.py --query "machine learning" --max-results 100
"""
import argparse
import sqlite3
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from urllib.request import urlopen
from datetime import datetime

ARXIV_API_URL = "http://export.arxiv.org/api/query"

def parse_arxiv_entry(entry: ET.Element) -> dict:
    """Parse a single arXiv entry from XML."""
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    
    paper_id = entry.find("atom:id", ns).text.split("/abs/")[-1]
    title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
    summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
    
    authors = []
    for author in entry.findall("atom:author", ns):
        name = author.find("atom:name", ns).text
        authors.append(name)
    
    published = entry.find("atom:published", ns).text[:10]
    updated = entry.find("atom:updated", ns).text[:10]
    
    categories = []
    for cat in entry.findall("atom:category", ns):
        categories.append(cat.get("term"))
    
    pdf_link = None
    html_link = None
    for link in entry.findall("atom:link", ns):
        if link.get("title") == "pdf":
            pdf_link = link.get("href")
        elif link.get("rel") == "alternate":
            html_link = link.get("href")
    
    return {
        "paper_id": paper_id,
        "title": title,
        "abstract": summary,
        "authors": ", ".join(authors),
        "categories": " ".join(categories),
        "published": published,
        "updated": updated,
        "url": html_link,
        "pdf_url": pdf_link,
    }

def fetch_arxiv_papers(query: str, max_results: int = 100, start: int = 0) -> list[dict]:
    """Fetch papers from arXiv API."""
    params = {
        "search_query": query,
        "start": start,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending"
    }
    
    url = f"{ARXIV_API_URL}?{urlencode(params)}"
    print(f"Fetching from: {url}")
    
    with urlopen(url) as response:
        xml_data = response.read()
    
    root = ET.fromstring(xml_data)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    
    papers = []
    for entry in root.findall("atom:entry", ns):
        try:
            paper = parse_arxiv_entry(entry)
            papers.append(paper)
        except Exception as e:
            print(f"Error parsing entry: {e}")
            continue
    
    return papers

def save_to_db(papers: list[dict], db_path: str = "papers.db") -> None:
    """Save papers to SQLite database."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Create table if it doesn't exist
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS papers (
            paper_id TEXT PRIMARY KEY,
            title TEXT,
            abstract TEXT,
            authors TEXT,
            categories TEXT,
            published TEXT,
            updated TEXT,
            url TEXT,
            pdf_url TEXT,
            fetched_at TEXT
        )
        """
    )
    
    # Insert papers
    fetched_at = datetime.now().isoformat()
    cur.executemany(
        """
        INSERT OR REPLACE INTO papers
        (paper_id, title, abstract, authors, categories, published, updated, url, pdf_url, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                p["paper_id"],
                p["title"],
                p["abstract"],
                p["authors"],
                p["categories"],
                p["published"],
                p["updated"],
                p["url"],
                p["pdf_url"],
                fetched_at,
            )
            for p in papers
        ],
    )
    
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    conn.close()
    
    print(f"Saved {len(papers)} papers. Total in DB: {count}")

def main():
    parser = argparse.ArgumentParser(description="Fetch papers from arXiv")
    parser.add_argument("--query", default="cat:cs.AI OR cat:cs.LG", help="arXiv search query")
    parser.add_argument("--max-results", type=int, default=100, help="Maximum number of results")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for fetching")
    parser.add_argument("--db", default="papers.db", help="Database path")
    
    args = parser.parse_args()
    
    total_fetched = 0
    start = 0
    
    while total_fetched < args.max_results:
        batch_size = min(args.batch_size, args.max_results - total_fetched)
        
        print(f"\nFetching batch {start // batch_size + 1} (papers {start} to {start + batch_size})...")
        papers = fetch_arxiv_papers(args.query, max_results=batch_size, start=start)
        
        if not papers:
            print("No more papers found.")
            break
        
        save_to_db(papers, args.db)
        total_fetched += len(papers)
        start += batch_size
        
        # Respect arXiv API rate limits (max 1 request per 3 seconds)
        if total_fetched < args.max_results:
            print("Waiting 3 seconds (arXiv API rate limit)...")
            time.sleep(3)
    
    print(f"\n✅ Fetching complete! Total papers fetched: {total_fetched}")
    print(f"Next step: Build BM25 index with 'uv run python scripts/01_build_bm25.py'")

if __name__ == "__main__":
    main()
