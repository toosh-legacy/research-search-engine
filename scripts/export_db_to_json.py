import sqlite3
import json
from pathlib import Path

def export(db_path: Path, out_path: Path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    rows = cur.execute("SELECT paper_id, title, abstract, authors, categories, primary_category, published, updated, url, pdf_url FROM papers").fetchall()
    conn.close()

    papers = []
    for r in rows:
        papers.append({
            "paper_id": r[0],
            "title": r[1],
            "abstract": r[2],
            "authors": r[3],
            "categories": r[4],
            "primary_category": r[5],
            "published": r[6],
            "updated": r[7],
            "url": r[8],
            "pdf_url": r[9],
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(papers)} papers to {out_path}")


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    db_path = repo_root / "papers.db"
    out_path = repo_root / "api" / "papers_data.json"
    export(db_path, out_path)
