"""
Fetch as many papers as possible from arXiv.

arXiv API Limitations:
- Maximum 30,000 results per query
- 3 second delay between requests (rate limiting)
- Best approach: Query by category and year to get around the 30k limit

Strategy:
- Fetch papers from all major categories
- Use date ranges to get historical papers
- Can potentially fetch 100k+ papers (limited by rate limits and time)
"""
import argparse
import sqlite3
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from urllib.request import urlopen
from datetime import datetime, timedelta
from pathlib import Path

ARXIV_API_URL = "http://export.arxiv.org/api/query"

# All major arXiv categories (60+ categories)
ALL_CATEGORIES = [
    # Computer Science
    "cs.AI", "cs.AR", "cs.CC", "cs.CE", "cs.CG", "cs.CL", "cs.CR", "cs.CV",
    "cs.CY", "cs.DB", "cs.DC", "cs.DL", "cs.DM", "cs.DS", "cs.ET", "cs.FL",
    "cs.GL", "cs.GR", "cs.GT", "cs.HC", "cs.IR", "cs.IT", "cs.LG", "cs.LO",
    "cs.MA", "cs.MM", "cs.MS", "cs.NA", "cs.NE", "cs.NI", "cs.OH", "cs.OS",
    "cs.PF", "cs.PL", "cs.RO", "cs.SC", "cs.SD", "cs.SE", "cs.SI", "cs.SY",
    
    # Mathematics
    "math.AC", "math.AG", "math.AP", "math.AT", "math.CA", "math.CO", "math.CT",
    "math.CV", "math.DG", "math.DS", "math.FA", "math.GM", "math.GN", "math.GR",
    "math.GT", "math.HO", "math.IT", "math.KT", "math.LO", "math.MG", "math.MP",
    "math.NA", "math.NT", "math.OA", "math.OC", "math.PR", "math.QA", "math.RA",
    "math.RT", "math.SG", "math.SP", "math.ST",
    
    # Physics
    "astro-ph.CO", "astro-ph.EP", "astro-ph.GA", "astro-ph.HE", "astro-ph.IM", "astro-ph.SR",
    "cond-mat.dis-nn", "cond-mat.mes-hall", "cond-mat.mtrl-sci", "cond-mat.other",
    "cond-mat.quant-gas", "cond-mat.soft", "cond-mat.stat-mech", "cond-mat.str-el",
    "gr-qc", "hep-ex", "hep-lat", "hep-ph", "hep-th",
    "math-ph", "nlin.AO", "nlin.CD", "nlin.CG", "nlin.PS", "nlin.SI",
    "nucl-ex", "nucl-th",
    "physics.acc-ph", "physics.ao-ph", "physics.app-ph", "physics.atm-clus",
    "physics.atom-ph", "physics.bio-ph", "physics.chem-ph", "physics.class-ph",
    "physics.comp-ph", "physics.data-an", "physics.ed-ph", "physics.flu-dyn",
    "physics.gen-ph", "physics.geo-ph", "physics.hist-ph", "physics.ins-det",
    "physics.med-ph", "physics.optics", "physics.plasm-ph", "physics.pop-ph",
    "physics.soc-ph", "physics.space-ph",
    "quant-ph",
    
    # Statistics
    "stat.AP", "stat.CO", "stat.ME", "stat.ML", "stat.OT", "stat.TH",
    
    # Quantitative Biology
    "q-bio.BM", "q-bio.CB", "q-bio.GN", "q-bio.MN", "q-bio.NC", "q-bio.OT",
    "q-bio.PE", "q-bio.QM", "q-bio.SC", "q-bio.TO",
    
    # Quantitative Finance
    "q-fin.CP", "q-fin.EC", "q-fin.GN", "q-fin.MF", "q-fin.PM", "q-fin.PR",
    "q-fin.RM", "q-fin.ST", "q-fin.TR",
    
    # Economics
    "econ.EM", "econ.GN", "econ.TH",
    
    # Electrical Engineering
    "eess.AS", "eess.IV", "eess.SP", "eess.SY",
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
    primary_cat = None
    if primary_category is not None:
        primary_cat = primary_category.get("term")
        categories.append(primary_cat)
    
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
        "categories": ", ".join(categories),
        "primary_category": primary_cat or (categories[0] if categories else ""),
        "published": published,
        "updated": updated,
        "url": html_link,
        "pdf_url": pdf_link,
    }

def save_to_db(papers: list[dict], db_path: Path):
    """Save papers to SQLite database."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    inserted = 0
    for paper in papers:
        cur.execute("""
            INSERT OR IGNORE INTO papers 
            (paper_id, title, abstract, authors, categories, primary_category, published, updated, url, pdf_url, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            paper["paper_id"],
            paper["title"],
            paper["abstract"],
            paper["authors"],
            paper["categories"],
            paper["primary_category"],
            paper["published"],
            paper["updated"],
            paper["url"],
            paper["pdf_url"],
        ))
        if cur.rowcount > 0:
            inserted += 1
    
    conn.commit()
    conn.close()
    return inserted

def fetch_papers_by_category_and_year(category: str, year: int, max_results: int = 1000):
    """Fetch papers for a specific category and year."""
    # Query for papers in this category published in this year
    query = f"cat:{category} AND submittedDate:[{year}0101 TO {year}1231]"
    
    params = {
        "search_query": query,
        "start": 0,
        "max_results": min(max_results, 2000),  # Fetch in chunks
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    url = f"{ARXIV_API_URL}?{urlencode(params)}"
    
    try:
        response = urlopen(url)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        
        papers = []
        for entry in entries:
            try:
                paper = parse_arxiv_entry(entry)
                papers.append(paper)
            except Exception as e:
                print(f"  ⚠️  Error parsing entry: {e}")
        
        return papers
    except Exception as e:
        print(f"  ❌ Error fetching {category} {year}: {e}")
        return []

def get_current_paper_count(db_path: Path) -> int:
    """Get current number of papers in database."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    count = cur.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    conn.close()
    return count

def main():
    parser = argparse.ArgumentParser(description="Fetch maximum papers from arXiv")
    parser.add_argument("--target", type=int, default=50000, 
                       help="Target number of papers (default: 50,000)")
    parser.add_argument("--per-category-year", type=int, default=500,
                       help="Max papers per category per year (default: 500)")
    parser.add_argument("--start-year", type=int, default=2018,
                       help="Start year (default: 2018)")
    parser.add_argument("--categories", nargs="+", default=None,
                       help="Specific categories to fetch (default: all)")
    
    args = parser.parse_args()
    
    repo_root = Path(__file__).resolve().parent.parent
    db_path = repo_root / "papers.db"
    
    if not db_path.exists():
        print("❌ Database not found. Run scripts/00_seed_sqlite.py first.")
        return
    
    categories = args.categories if args.categories else ALL_CATEGORIES
    current_year = datetime.now().year
    years = range(args.start_year, current_year + 1)
    
    initial_count = get_current_paper_count(db_path)
    print(f"📊 Current papers in database: {initial_count:,}")
    print(f"🎯 Target: {args.target:,} papers")
    print(f"📚 Categories: {len(categories)}")
    print(f"📅 Years: {args.start_year}-{current_year} ({len(years)} years)")
    print(f"⏱️  Estimated time: {(len(categories) * len(years) * 3) / 3600:.1f} hours")
    print(f"\n🚀 Starting massive fetch...\n")
    
    total_fetched = 0
    total_inserted = 0
    start_time = time.time()
    
    for cat_idx, category in enumerate(categories, 1):
        if total_inserted + initial_count >= args.target:
            print(f"\n✅ Reached target of {args.target:,} papers!")
            break
        
        for year in years:
            current_count = get_current_paper_count(db_path)
            if current_count >= args.target:
                print(f"\n✅ Reached target of {args.target:,} papers!")
                break
            
            print(f"[{cat_idx}/{len(categories)}] Fetching {category} {year}...", end=" ", flush=True)
            
            papers = fetch_papers_by_category_and_year(category, year, args.per_category_year)
            
            if papers:
                inserted = save_to_db(papers, db_path)
                total_fetched += len(papers)
                total_inserted += inserted
                
                elapsed = time.time() - start_time
                rate = total_fetched / elapsed if elapsed > 0 else 0
                remaining = max(0, args.target - current_count)
                eta_seconds = remaining / rate if rate > 0 else 0
                eta_hours = eta_seconds / 3600
                
                print(f"✓ {len(papers)} fetched, {inserted} new | "
                      f"Total: {current_count:,} | "
                      f"Rate: {rate:.1f}/s | "
                      f"ETA: {eta_hours:.1f}h")
            else:
                print(f"⊘ No papers")
            
            # Rate limiting (3 seconds between requests)
            time.sleep(3)
    
    final_count = get_current_paper_count(db_path)
    elapsed = time.time() - start_time
    
    print(f"\n" + "="*70)
    print(f"✅ Fetch Complete!")
    print(f"📊 Papers in database: {initial_count:,} → {final_count:,} (+{final_count - initial_count:,})")
    print(f"📥 Total fetched: {total_fetched:,} papers")
    print(f"⏱️  Time elapsed: {elapsed/3600:.1f} hours")
    print(f"⚡ Average rate: {total_fetched/elapsed:.1f} papers/second")
    print(f"\n🔨 Next step: Rebuild the search index")
    print(f"   uv run python scripts/01_build_bm25.py")
    print("="*70)

if __name__ == "__main__":
    main()
