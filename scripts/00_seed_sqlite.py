import sqlite3
import json
from pathlib import Path

# This script seeds a SQLite database at the repository root named 'papers.db'.
# It prefers to load JSON data if available (api/papers_data.json or papers_data.json),
# otherwise it falls back to a small SAMPLE for quick testing.

SAMPLE = [
    {
        "paper_id": "p1",
        "title": "Attention Is All You Need",
        "abstract": "We propose the Transformer, a model architecture based solely on attention mechanisms.",
        "authors": "Vaswani, Shazeer, Parmar",
        "categories": "cs.CL cs.LG",
        "published": "2017-06-12",
        "updated": "2017-12-05",
        "url": "https://arxiv.org/abs/1706.03762",
        "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
    }
]


def load_json_data(repo_root: Path) -> list[dict]:
    # Prefer api/papers_data.json, then top-level papers_data.json
    candidates = [repo_root / "api" / "papers_data.json", repo_root / "papers_data.json"]
    for p in candidates:
        if p.exists():
            print(f"Loading JSON data from {p}")
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Normalize keys if needed
            normalized = []
            for item in data:
                # support both 'id' and 'paper_id'
                pid = item.get("paper_id") or item.get("id")
                normalized.append({
                    "paper_id": pid,
                    "title": item.get("title", ""),
                    "abstract": item.get("abstract", ""),
                    "authors": item.get("authors", ""),
                    "categories": item.get("category") or item.get("categories") or "",
                    "published": item.get("published") or item.get("date") or "",
                    "updated": item.get("updated", ""),
                    "url": item.get("url", ""),
                    "pdf_url": item.get("pdf_url") or item.get("pdf", ""),
                })
            return normalized
    print("No JSON data found; falling back to SAMPLE")
    return SAMPLE


def ensure_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
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
    cur.execute("CREATE INDEX IF NOT EXISTS idx_primary_category ON papers(primary_category)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_published ON papers(published)")
    conn.commit()


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    db_path = repo_root / "papers.db"

    data = load_json_data(repo_root)

    conn = sqlite3.connect(db_path)
    ensure_schema(conn)
    cur = conn.cursor()

    rows = []
    for p in data:
        primary = ""
        if p.get("categories"):
            # categories may be space or comma separated
            cats = [c.strip() for c in __import__("re").split(r"[\s,]+", p["categories"]) if c.strip()]
            primary = cats[0] if cats else ""
        rows.append(
            (
                p.get("paper_id"),
                p.get("title"),
                p.get("abstract"),
                p.get("authors"),
                p.get("categories"),
                primary,
                p.get("published"),
                p.get("updated"),
                p.get("url"),
                p.get("pdf_url"),
                "1970-01-01T00:00:00",
            )
        )

    cur.executemany(
        """
        INSERT OR REPLACE INTO papers
        (paper_id, title, abstract, authors, categories, primary_category, published, updated, url, pdf_url, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    conn.commit()
    conn.close()
    print(f"Seeded SQLite with {len(rows)} papers -> {db_path}")


if __name__ == "__main__":
    main()
