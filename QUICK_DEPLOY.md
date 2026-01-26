# Quick Deploy Guide - Get Your Search Engine Running on Vercel

Follow these steps to deploy your arXiv search engine with all 80,000+ papers:

## Step 1: Export All Papers (Run Locally)

```bash
python export_for_vercel.py
```

This will:
- Export ALL papers from `papers.db` to JSON
- Create `api/papers_data.json` (uncompressed, ~100-200MB)
- Create `api/papers_data.json.gz` (compressed, ~20-40MB)

**Time:** 2-5 minutes depending on database size

## Step 2: Upload Compressed File to GitHub Releases

### Option A: Using GitHub Web Interface (Easiest)

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/arXive-intelli`
2. Click **"Releases"** → **"Create a new release"**
3. Tag version: `v1.0.0` (or any version)
4. Release title: `Full Papers Database`
5. Click **"Attach binaries"** or drag and drop `api/papers_data.json.gz`
6. Click **"Publish release"**
7. After publishing, right-click on `papers_data.json.gz` → **"Copy link address"**
   - URL format: `https://github.com/USERNAME/REPO/releases/download/v1.0.0/papers_data.json.gz`

### Option B: Using GitHub CLI

```bash
gh release create v1.0.0 api/papers_data.json.gz --title "Full Papers Database"
```

Then get the URL from the release page.

## Step 3: Set Vercel Environment Variables

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to **Settings** → **Environment Variables**

**Important:** The frontend and API are both on the same Vercel app. The frontend calls `/api/*` on your Vercel URL (same origin). **Do NOT set `REACT_APP_API_URL`** — and **delete it if it exists** (e.g. `https://your-backend-api.com`). That placeholder causes CORS errors and "Failed to fetch".

4. Add **only** this variable:
   - **Key**: `PAPERS_DATA_URL`
   - **Value**: The GitHub Releases URL from Step 2
   - **Environment**: Production (and Preview if you want)
5. Click **"Save"**
6. **Remove** `REACT_APP_API_URL` if present (⋯ → Delete).

## Step 4: Deploy to Vercel

### If you haven't connected to Vercel yet:

1. Go to [Vercel](https://vercel.com)
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Vercel will auto-detect the configuration
5. Click **"Deploy"**

### If already connected:

Just push your code:
```bash
git add .
git commit -m "Add full database support with external storage"
git push
```

Vercel will automatically redeploy.

## Step 5: Verify It Works

1. Wait for deployment to complete (2-3 minutes)
2. Visit your Vercel URL: `https://your-app.vercel.app`
3. Check health endpoint: `https://your-app.vercel.app/api/health`

You should see:
```json
{
  "status": "ok",
  "papers_loaded": 80000,  // Your actual count
  "bm25_loaded": false,
  "data_path": "/var/task/api/papers_data.json",
  "data_exists": true
}
```

4. Try a search! It should now search through all your papers.

## Troubleshooting

### CORS / "Failed to fetch" / "your-backend-api.com"

You see `Access to fetch at 'https://your-backend-api.com/api/...' has been blocked by CORS policy`.

- **Cause:** `REACT_APP_API_URL` is set to a placeholder like `https://your-backend-api.com`. The real API lives on your Vercel app at `https://your-app.vercel.app/api/...`.
- **Fix:** In Vercel → Project → **Settings** → **Environment Variables**, **delete** `REACT_APP_API_URL`. Redeploy. The frontend will use same-origin (`/api/...`) and CORS goes away.

### "papers_loaded: 0"
- Check Vercel function logs (Dashboard → Your Project → Functions → View Logs)
- Verify `PAPERS_DATA_URL` is set correctly
- Test the URL in a browser (should download the file)

### "Failed to download papers data"
- Make sure the GitHub Releases URL is publicly accessible
- Check the URL format is correct
- Try downloading the file manually to verify it works

### Slow first request
- Normal! First request downloads and decompresses the file (~30-60 seconds)
- Subsequent requests will be fast (file is cached)

### Memory errors
- Vercel Hobby plan: 1024MB memory limit
- If you hit limits, consider:
  - Using Vercel Pro (3008MB)
  - Or reduce the number of papers exported

## What Happens Behind the Scenes

1. **First Request**: API downloads `papers_data.json.gz` from GitHub Releases
2. **Decompression**: File is decompressed to JSON
3. **Caching**: Decompressed file is saved locally for future use
4. **Loading**: All papers are loaded into memory
5. **Ready**: Search engine is ready to use!

Subsequent deployments will reuse the cached file, so they'll be faster.

## Next Steps (Optional)

- **Add BM25 Index**: Upload `app/bm25.pkl` to external storage and set `BM25_URL` env var for faster searches
- **Monitor Performance**: Check Vercel Analytics for usage stats
- **Set Custom Domain**: Add your own domain in Vercel settings

---

**That's it!** Your search engine should now be running with all 80,000+ papers! 🚀
