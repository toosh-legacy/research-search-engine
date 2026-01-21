import pickle
from socket import close
import sqlite3
from rank_bm25 import BM25Okapi

def tokenize(text:str) -> list[str]:
    return text.lower().split()

def main()-> None:
    conn = sqlite3.connect("papers.db")
    cur = conn.cursor()
    cur.execute("SELECT paper_id, title, abstract FROM papers")
    rows = cur.fetchall()
    conn,close()

    doc_ids: list[str] = []
    corpus: list[list[str]] = []

    for pid, title, abstract in rows:
        doc_ids.append(pid)
        corpus.append(tokenize(f"{title} {abstract}"))

    bm25 = BM25Okapi(corpus)

    with open("bm25.pkl", "wb") as f:
        pickle.dump({"doc_ids": doc_ids, "bm25": bm25}, f)
    
    print(f"Built Bm25 for {len(doc_ids)} documents -> bm25.pkl")



if __name__ == "__main__":
    main()