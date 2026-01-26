# Debugging "Failed to fetch" and API Errors

When you see **"Failed to fetch"** or **"Search failed"**, use the steps below to capture logs and debug.

---

## 1. Browser logs (frontend)

1. Open your app (localhost or Vercel URL).
2. Open **DevTools**: press **F12** (or right‑click → Inspect → **Console**).
3. Reproduce the error (e.g. run a search, or just load the page).
4. In the Console, look for lines starting with **`[arXiv-Intelli API]`**. They look like:
   ```json
   [arXiv-Intelli API] {
     "tag": "request",
     "url": "https://your-app.vercel.app/api/search?q=...",
     "base": "",
     "ts": "2025-01-26T..."
   }
   ```
   or:
   ```json
   [arXiv-Intelli API] {
     "tag": "network_error",
     "error": "Failed to fetch",
     "url": "https://...",
     "hint": "Network error: API unreachable, CORS, or wrong URL..."
   }
   ```
5. **Copy all `[arXiv-Intelli API]` log objects** and paste them when reporting the bug (e.g. in a GitHub issue or to your dev).

---

## 2. Vercel function logs (backend, production only)

If the app is on Vercel and the frontend shows "Failed to fetch":

1. Go to [Vercel Dashboard](https://vercel.com/dashboard) → your project.
2. Open **Logs** or **Functions** → select the function (e.g. `api/index`) → **View logs**.
3. Trigger the error again (e.g. visit `/api/health` or run a search).
4. Copy the **relevant log lines** (errors, stack traces, "Loading papers...", "Failed to download...", etc.) and share them.

---

## 3. Quick checks

| Symptom | What to check |
|--------|----------------|
| **Failed to fetch** (browser) | Wrong API URL, API down, or CORS. Check `[arXiv-Intelli API]` → `url` and `base`. |
| **404 on /api/...** | Routing: `vercel.json` routes `/api/*` to `api/index.py`. Confirm deployment includes the API. |
| **Stats/search never load** | Backend not responding. Test `https://your-app.vercel.app/api/health` in the browser. |
| **`papers_loaded: 0`** | Data not loaded. Check `PAPERS_DATA_URL` in Vercel env vars and Vercel function logs. |
| **CORS errors in Console** | Often caused by `REACT_APP_API_URL` set to a **separate** backend (e.g. `https://your-backend-api.com`). When frontend + API are both on Vercel, **remove** `REACT_APP_API_URL` so the app uses same-origin `/api/...`. |

---

## 4. Local development

- **Frontend**: `cd frontend && npm start` → typically `http://localhost:3000`.
- **API base URL**: dev uses `http://localhost:8001` unless `REACT_APP_API_URL` is set.
- Run the API (or point `REACT_APP_API_URL` at your deployed API), then check the browser Console for `[arXiv-Intelli API]` logs as above.

---

## 5. What to share when reporting a bug

Please include:

1. **Where it happens**: Local dev or Vercel URL.
2. **Exact error message** from the UI (e.g. "Failed to fetch: ...").
3. **All `[arXiv-Intelli API]` logs** from the browser Console (copy/paste).
4. **Any relevant Vercel function logs** (if on Vercel).
5. **What you did**: e.g. "Clicked Search", "Page load", "Called /api/health".

That will make it much easier to track down the cause.
