// API service for communicating with FastAPI backend

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const searchPapers = async (query, filters = {}) => {
  const params = new URLSearchParams({
    q: query,
    k: filters.limit || 10,
    sort: filters.sort || 'relevance',
    semantic: filters.semantic !== false ? 'true' : 'false',
  });

  if (filters.category) params.append('category', filters.category);
  if (filters.yearFrom) params.append('year_from', filters.yearFrom);
  if (filters.yearTo) params.append('year_to', filters.yearTo);
  if (filters.author) params.append('author', filters.author);

  const response = await fetch(`${API_BASE_URL}/search?${params}`);
  if (!response.ok) {
    throw new Error('Search failed');
  }
  return response.json();
};

export const getStats = async () => {
  const response = await fetch(`${API_BASE_URL}/stats`);
  if (!response.ok) {
    throw new Error('Failed to fetch stats');
  }
  return response.json();
};

export const getFacets = async () => {
  const response = await fetch(`${API_BASE_URL}/facets`);
  if (!response.ok) {
    throw new Error('Failed to fetch facets');
  }
  return response.json();
};

export const getSuggestions = async (query) => {
  const params = new URLSearchParams({ q: query });
  const response = await fetch(`${API_BASE_URL}/suggestions?${params}`);
  if (!response.ok) {
    throw new Error('Failed to fetch suggestions');
  }
  return response.json();
};
