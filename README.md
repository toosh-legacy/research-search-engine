# arXiv-Intelli - Research Paper Search Engine

A full-featured search engine for academic research papers from arXiv, deployed on Vercel with support for 80,000+ papers.

## ✨ Features

- 🔍 **Full-text BM25 Search** - Fast and relevant results
- 🎯 **Advanced Filtering** - Filter by category, year, author
- 📊 **Statistics Dashboard** - Overview of your paper collection
- 🎨 **Modern Web UI** - Clean, responsive React interface
- 🚀 **Vercel Deployment** - Serverless deployment with external storage
- ⚡ **Fast & Scalable** - Handles 80k+ papers efficiently

## 🚀 Quick Deploy to Vercel

See **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** for step-by-step deployment instructions.

### Quick Summary:

1. **Export papers**: `python export_for_vercel.py`
2. **Upload to GitHub Releases**: Upload `api/papers_data.json.gz`
3. **Set Vercel env var**: Add `PAPERS_DATA_URL` with the download URL
4. **Deploy**: Push to GitHub and Vercel auto-deploys!

## 📁 Project Structure

```
├── api/
│   ├── index.py          # FastAPI serverless function
│   ├── requirements.txt  # Python dependencies
│   └── papers_data.json  # Papers data (downloaded at runtime)
├── frontend/
│   └── src/              # React frontend
├── export_for_vercel.py  # Script to export papers from database
├── vercel.json           # Vercel configuration
└── QUICK_DEPLOY.md       # Deployment guide
```

## 🔧 Local Development

### Prerequisites
- Python 3.8+
- Node.js 16+

### Backend
```bash
cd api
pip install -r requirements.txt
# The API will load papers_data.json if available locally
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## 📚 Documentation

- **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** - Complete deployment guide
- **API Routes**: `/api/search`, `/api/stats`, `/api/facets`, `/api/health`

## 🛠️ Technologies

- **FastAPI** - Python web framework
- **React** - Frontend framework
- **BM25 (rank-bm25)** - Search ranking algorithm
- **Vercel** - Serverless hosting platform
