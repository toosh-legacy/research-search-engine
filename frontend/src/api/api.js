// API service for communicating with FastAPI backend

const API_BASE_URL = process.env.REACT_APP_API_URL || (
  process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8001'
);

/**
 * Debug logger: always logs to console. Copy this output when reporting "Failed to fetch" etc.
 * In production, open DevTools (F12) → Console to see these logs.
 */
export function logDebug(tag, data) {
  const payload = { tag, ...data, ts: new Date().toISOString() };
  console.log('[arXiv-Intelli API]', JSON.stringify(payload, null, 2));
  return payload;
}

async function fetchWithDebug(url, opts = {}) {
  const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`;
  logDebug('request', { url: fullUrl, base: API_BASE_URL || '(same-origin)' });

  try {
    const res = await fetch(fullUrl, { ...opts, mode: 'cors' });
    const contentType = res.headers.get('content-type') || '';
    let body = null;
    try {
      if (contentType.includes('application/json')) {
        body = await res.json();
      } else {
        body = await res.text();
      }
    } catch (_) {
      body = await res.text().catch(() => null);
    }

    if (!res.ok) {
      const errPayload = {
        status: res.status,
        statusText: res.statusText,
        url: fullUrl,
        body: body ?? '(empty)',
      };
      logDebug('error_response', errPayload);
      const msg = typeof body === 'object' && body?.detail
        ? (Array.isArray(body.detail) ? body.detail.map((d) => d.msg || JSON.stringify(d)).join('; ') : body.detail)
        : `HTTP ${res.status}: ${res.statusText}`;
      throw new Error(msg);
    }

    return body;
  } catch (e) {
    if (e instanceof TypeError && e.message === 'Failed to fetch') {
      const errPayload = {
        error: 'Failed to fetch',
        url: fullUrl,
        base: API_BASE_URL || '(same-origin)',
        hint: 'Network error: API unreachable, CORS, or wrong URL. Check DEBUG.md for logs.',
      };
      logDebug('network_error', errPayload);
      throw new Error(
        `Failed to fetch: ${fullUrl}. Check browser Console (F12) for details, or see DEBUG.md.`
      );
    }
    throw e;
  }
}

export const searchPapers = async (query, filters = {}) => {
  const params = new URLSearchParams({
    q: query,
    limit: filters.limit || 10,
    sort_by: filters.sort || 'relevance',
    semantic: filters.semantic !== false ? 'true' : 'false',
  });
  if (filters.category) params.append('category', filters.category);
  if (filters.yearFrom) params.append('year_min', filters.yearFrom);
  if (filters.yearTo) params.append('year_max', filters.yearTo);
  if (filters.author) params.append('author', filters.author);

  return fetchWithDebug(`/api/search?${params}`);
};

export const getStats = async () => fetchWithDebug('/api/stats');

export const getFacets = async () => fetchWithDebug('/api/facets');

export const getSuggestions = async (query) => {
  const params = new URLSearchParams({ q: query });
  return fetchWithDebug(`/api/suggestions?${params}`);
};
