import sqlite3

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
    },
    {
        "paper_id": "p2",
        "title": "A Survey on Graph Neural Networks",
        "abstract": "This survey provides a comprehensive overview of graph neural networks and their applications.",
        "authors": "Wu, Pan, Chen",
        "categories": "cs.LG",
        "published": "2019-01-01",
        "updated": "2020-10-01",
        "url": "https://arxiv.org/abs/1901.00596",
        "pdf_url": "https://arxiv.org/pdf/1901.00596.pdf",
    },
    {
        "paper_id": "p3",
        "title": "Deep Reinforcement Learning with Double Q-learning",
        "abstract": "We show how to reduce overestimation by decoupling action selection and evaluation in Q-learning.",
        "authors": "van Hasselt, Guez, Silver",
        "categories": "cs.LG cs.AI",
        "published": "2015-09-01",
        "updated": "2016-01-01",
        "url": "https://arxiv.org/abs/1509.06461",
        "pdf_url": "https://arxiv.org/pdf/1509.06461.pdf",
    },
]

def main() -> None:
    conn = sqlite3.connect("papers.db")
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
    
    # Create indexes for fast filtering
    cur.execute("CREATE INDEX IF NOT EXISTS idx_primary_category ON papers(primary_category)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_published ON papers(published)")

    cur.executemany(
        """
        INSERT OR REPLACE INTO papers
        (paper_id, title, abstract, authors, categories, primary_category, published, updated, url, pdf_url, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                p["paper_id"],
                p["title"],
                p["abstract"],
                p["authors"],
                p["categories"],
                p["categories"].split()[0],  # First category as primary
                p["published"],
                p["updated"],
                p["url"],
                p["pdf_url"],
                "2024-01-01T00:00:00",
            )
            for p in SAMPLE
        ],
    )

    conn.commit()
    conn.close()
    print(f"Seeded SQLite with {len(SAMPLE)} papers -> papers.db")

if __name__ == "__main__":
    main()
