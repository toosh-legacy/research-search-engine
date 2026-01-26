"""
Bulk fetch papers from arXiv with progress tracking and resumability.
Fetches from multiple categories to get diverse papers.
"""
import argparse
import sqlite3
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from urllib.request import urlopen
from datetime import datetime
from pathlib import Path

ARXIV_API_URL = "http://export.arxiv.org/api/query"

# Diverse research categories across multiple fields
CATEGORIES = [
    # Computer Science - AI/ML
    "cs.AI",      # Artificial Intelligence
    "cs.LG",      # Machine Learning  
    "cs.CV",      # Computer Vision
    "cs.CL",      # Computation and Language
    "cs.NE",      # Neural and Evolutionary Computing
    "cs.RO",      # Robotics
    
    # Computer Science - Systems
    "cs.CR",      # Cryptography and Security
    "cs.DB",      # Databases
    "cs.DS",      # Data Structures and Algorithms
    "cs.SE",      # Software Engineering
    "cs.DC",      # Distributed, Parallel, and Cluster Computing
    "cs.PL",      # Programming Languages
    
    # Statistics & Math
    "stat.ML",    # Statistics - Machine Learning
    "stat.ME",    # Methodology
    "math.OC",    # Optimization and Control
    "math.ST",    # Statistics Theory
    "math.NA",    # Numerical Analysis
    
    # Physics
    "physics.comp-ph",  # Computational Physics
    "physics.data-an",  # Data Analysis
    "astro-ph.IM",      # Instrumentation and Methods for Astrophysics
    
    # Quantitative Biology
    "q-bio.QM",   # Quantitative Methods
    "q-bio.GN",   # Genomics
    "q-bio.NC",   # Neurons and Cognition
    
    # Economics & Finance
    "econ.EM",    # Econometrics
    "q-fin.ST",   # Statistical Finance
    "q-fin.CP",   # Computational Finance
]

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
    primary_category = entry.find("arxiv:primary_category", ns)
    if primary_category is not None:
        categories.append(primary_category.get("term"))
    
    for cat in entry.findall("atom:category", ns):
        term = cat.get("term")
        if term not in categories:
            categories.append(term)
    
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
        "primary_category": categories[0] if categories else "",
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
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    url = f"{ARXIV_API_URL}?{urlencode(params)}"
    
    try:
        with urlopen(url, timeout=30) as response:
            xml_data = response.read()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []
    
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

def save_to_db(papers: list[dict], db_path: str = "papers.db") -> int:
    """Save papers to SQLite database. Returns number of new papers added."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Ensure table has all columns
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS papers (
            paper_id TEXT PRIMARY KEY,
            title TEXT,
            abstract TEXT,
            authors TEXT,
            categories TEXT,
            primary_category TEXT,
            published TEXT,
            updated TEXT,
            url TEXT,
            pdf_url TEXT,
            fetched_at TEXT
        )
        """
    )
    
    fetched_at = datetime.now().isoformat()
    new_count = 0
    
    for p in papers:
        try:
            cur.execute(
                """
                INSERT OR IGNORE INTO papers
                (paper_id, title, abstract, authors, categories, primary_category, published, updated, url, pdf_url, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    p["paper_id"],
                    p["title"],
                    p["abstract"],
                    p["authors"],
                    p["categories"],
                    p.get("primary_category", ""),
                    p["published"],
                    p["updated"],
                    p["url"],
                    p["pdf_url"],
                    fetched_at,
                )
            )
            if cur.rowcount > 0:
                new_count += 1
        except Exception as e:
            print(f"Error inserting paper {p.get('paper_id')}: {e}")
    
    conn.commit()
    total_count = cur.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    conn.close()
    
    return new_count, total_count

def main():
    parser = argparse.ArgumentParser(description="Bulk fetch papers from arXiv")
    parser.add_argument("--target", type=int, default=80000, help="Target number of papers")
    parser.add_argument("--batch-size", type=int, default=100, help="Papers per API call")
    parser.add_argument("--db", default="papers.db", help="Database path")
    parser.add_argument("--resume", action="store_true", help="Resume from existing database")
    
    args = parser.parse_args()
    
    # Check current count
    if Path(args.db).exists():
        conn = sqlite3.connect(args.db)
        current_count = conn.cursor().execute("SELECT COUNT(*) FROM papers").fetchone()[0]
        conn.close()
        print(f"📊 Current database: {current_count:,} papers")
    else:
        current_count = 0
        print("📊 Starting fresh database")
    
    if current_count >= args.target:
        print(f"✅ Already have {current_count:,} papers (target: {args.target:,})")
        return
    
    remaining = args.target - current_count
    print(f"🎯 Target: {args.target:,} papers ({remaining:,} remaining)")
    print(f"⏱️  Estimated time: {(remaining / args.batch_size * 3) / 60:.1f} minutes")
    print(f"\nFetching from {len(CATEGORIES)} categories...")
    
    total_fetched = 0
    category_idx = 0
    papers_per_category = remaining // len(CATEGORIES) + 1
    
    start_time = time.time()
    
    for category in CATEGORIES:
        print(f"\n📚 Fetching from {category}...")
        
        for start in range(0, papers_per_category, args.batch_size):
            if total_fetched >= remaining:
                break
            
            batch_size = min(args.batch_size, remaining - total_fetched)
            query = f"cat:{category}"
            
            print(f"  Fetching {start}-{start+batch_size}... ", end="", flush=True)
            papers = fetch_arxiv_papers(query, max_results=batch_size, start=start)
            
            if not papers:
                print("No more papers")
                break
            
            new_count, db_total = save_to_db(papers, args.db)
            total_fetched += new_count
            
            elapsed = time.time() - start_time
            rate = total_fetched / elapsed if elapsed > 0 else 0
            eta = (remaining - total_fetched) / rate if rate > 0 else 0
            
            print(f"✓ {new_count} new | Total: {db_total:,} | Rate: {rate:.1f}/s | ETA: {eta/60:.1f}m")
            
            if total_fetched >= remaining:
                break
            
            # Respect rate limit (3 seconds between requests)
            time.sleep(3)
    
    elapsed = time.time() - start_time
    print(f"\n✅ Fetching complete!")
    print(f"📊 Total papers in database: {db_total:,}")
    print(f"⏱️  Time taken: {elapsed/60:.1f} minutes")
    print(f"\n🔨 Next step: Build index with 'uv run python scripts/01_build_bm25.py'")

if __name__ == "__main__":
    main()
