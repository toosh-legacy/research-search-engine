# Fetching Maximum Papers from arXiv

## 🎯 Goal: Get as many papers as possible (towards your 80k target)

## Understanding arXiv Limits

arXiv has **millions of papers**, but their API has some constraints:
- **30,000 result limit** per single query
- **3 second rate limit** between requests
- Best strategy: Query by category + year to bypass the 30k limit

## 📊 What's Possible

With the new `fetch_all_arxiv.py` script:
- **150+ categories** across all fields
- **Query by year** (2018-2026) to get more papers per category
- **Estimated capacity**: 50,000-100,000+ papers
- **Time required**: 10-30 hours depending on target

## 🚀 Quick Start

### Option 1: Fetch 10,000 Papers (Fast - ~3 hours)
```powershell
uv run python scripts/fetch_all_arxiv.py --target 10000 --per-category-year 200 --start-year 2020
```

### Option 2: Fetch 50,000 Papers (Recommended - ~15 hours)
```powershell
uv run python scripts/fetch_all_arxiv.py --target 50000 --per-category-year 500 --start-year 2018
```

### Option 3: Fetch Maximum (~80k+ papers - ~24 hours)
```powershell
uv run python scripts/fetch_all_arxiv.py --target 80000 --per-category-year 800 --start-year 2015
```

## 📝 Parameters Explained

- `--target`: Total number of papers you want (default: 50,000)
- `--per-category-year`: Max papers per category per year (default: 500)
- `--start-year`: Starting year for fetching (default: 2018)
- `--categories`: Specific categories to fetch (optional, default: all 150+)

## 🎨 Categories Included

The script fetches from **150+ categories** across all major fields:

### Computer Science (40 categories)
- AI/ML: cs.AI, cs.LG, cs.CV, cs.CL, cs.NE, cs.RO
- Systems: cs.CR, cs.DB, cs.DC, cs.OS, cs.PF, cs.SE
- Theory: cs.CC, cs.DS, cs.FL, cs.GT, cs.LO
- And many more...

### Mathematics (33 categories)
- math.AC, math.AG, math.AP, math.AT, math.CA, math.CO, math.CT
- math.DG, math.DS, math.FA, math.NT, math.OC, math.PR, math.ST
- And many more...

### Physics (50+ categories)
- Astrophysics: astro-ph.CO, astro-ph.GA, astro-ph.HE
- Condensed Matter: cond-mat.*
- High Energy Physics: hep-ex, hep-lat, hep-ph, hep-th
- Quantum Physics: quant-ph
- And many more...

### Biology (10 categories)
- q-bio.BM, q-bio.CB, q-bio.GN, q-bio.NC, q-bio.QM
- And more...

### Finance & Economics (12 categories)
- q-fin.CP, q-fin.EC, q-fin.ST, econ.EM
- And more...

### Electrical Engineering (4 categories)
- eess.AS, eess.IV, eess.SP, eess.SY

## 💡 Smart Fetching Strategy

The script is smart about fetching:
1. **Checks existing papers**: Won't re-fetch duplicates
2. **Progress tracking**: Shows real-time progress with ETA
3. **Category + Year**: Queries each category for each year separately
4. **Rate limiting**: Respects arXiv's 3-second rule
5. **Resumable**: Stop and resume anytime

## 📈 Example Session

```powershell
PS> uv run python scripts/fetch_all_arxiv.py --target 20000

📊 Current papers in database: 3,309
🎯 Target: 20,000 papers
📚 Categories: 150
📅 Years: 2018-2026 (9 years)
⏱️  Estimated time: 11.3 hours

🚀 Starting massive fetch...

[1/150] Fetching cs.AI 2018... ✓ 487 fetched, 423 new | Total: 3,732 | Rate: 23.4/s | ETA: 11.2h
[1/150] Fetching cs.AI 2019... ✓ 512 fetched, 476 new | Total: 4,208 | Rate: 24.1/s | ETA: 10.8h
[1/150] Fetching cs.AI 2020... ✓ 531 fetched, 501 new | Total: 4,709 | Rate: 23.8/s | ETA: 10.5h
...
```

## 🔨 After Fetching

Once you have your papers, rebuild the search index:

```powershell
uv run python scripts/01_build_bm25.py
```

This will update the search index to include all new papers.

## ⚡ Performance Tips

1. **Run overnight**: Large fetches take many hours
2. **Stable connection**: Ensure internet is stable
3. **Check progress**: Script shows real-time statistics
4. **Start small**: Try 10k first, then go bigger
5. **Resume if needed**: Script can resume from where it stopped

## 🎯 Targeted Fetching

Want specific fields only? Specify categories:

```powershell
# Only Computer Science
uv run python scripts/fetch_all_arxiv.py --target 20000 --categories cs.AI cs.LG cs.CV cs.CL cs.RO cs.CR

# Only Physics
uv run python scripts/fetch_all_arxiv.py --target 15000 --categories quant-ph hep-th hep-ph astro-ph.CO

# Only Biology & Medicine
uv run python scripts/fetch_all_arxiv.py --target 10000 --categories q-bio.GN q-bio.NC q-bio.QM
```

## 📊 Monitoring Progress

The script shows:
- **Current category** being fetched
- **Papers fetched** vs **papers added** (deduplication)
- **Total papers** in database
- **Fetch rate** (papers/second)
- **ETA** (estimated time remaining)

## 🛑 Stopping and Resuming

- Press `Ctrl+C` to stop anytime
- Run the same command again - it will resume automatically
- The script checks existing papers and skips duplicates

## 🎉 Expected Results

| Target | Categories | Years | Time | Storage |
|--------|-----------|-------|------|---------|
| 10k    | 150       | 3 yrs | 3h   | ~100MB  |
| 25k    | 150       | 5 yrs | 8h   | ~250MB  |
| 50k    | 150       | 7 yrs | 15h  | ~500MB  |
| 80k    | 150       | 9 yrs | 24h  | ~800MB  |

## 🚀 Start Your Massive Fetch!

Pick your target and run:

```powershell
# For your 80k goal (will run ~24 hours)
uv run python scripts/fetch_all_arxiv.py --target 80000 --per-category-year 800 --start-year 2015
```

The search engine will become incredibly comprehensive with research from all major scientific fields!

---

**Note**: The script is designed to be efficient and respectful of arXiv's servers. It follows all rate limiting guidelines and will not cause any issues.
