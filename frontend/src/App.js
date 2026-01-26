import React, { useState, useEffect } from 'react';
import './App.css';
import SearchBar from './components/SearchBar';
import FilterModal from './components/FilterModal';
import ResultsList from './components/ResultsList';
import StatsPanel from './components/StatsPanel';
import { searchPapers, getStats, getFacets } from './api/api';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    category: '',
    yearFrom: '',
    yearTo: '',
    author: '',
    sort: 'relevance',
    semantic: true,
    limit: 10,
  });
  const [stats, setStats] = useState(null);
  const [facets, setFacets] = useState(null);
  const [searchInfo, setSearchInfo] = useState(null);

  useEffect(() => {
    getStats().then(setStats).catch((e) => {
      console.error('[arXiv-Intelli] getStats failed', e);
    });
    getFacets().then(setFacets).catch((e) => {
      console.error('[arXiv-Intelli] getFacets failed', e);
    });
  }, []);

  const handleSearch = async (searchQuery) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);
    
    try {
      const data = await searchPapers(searchQuery, filters);
      setResults(data.results || []);
      setSearchInfo(data);
    } catch (err) {
      setError(err.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    if (query) {
      handleSearch(query);
    }
  };

  return (
    <div className="App">
      <div className="header">
        <div className="header-content">
          <h1>arXiv-Intelli</h1>
          <p className="subtitle">AI-powered semantic search across 80,000+ research papers</p>
        </div>
      </div>

      <div className="search-container">
        <SearchBar
          query={query}
          setQuery={setQuery}
          onSearch={handleSearch}
          onOpenFilters={() => setShowFilters(true)}
          loading={loading}
        />
      </div>

      {stats && <StatsPanel stats={stats} />}

      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
          <p className="error-hint">Open DevTools (F12) → Console, look for <code>[arXiv-Intelli API]</code> logs. Copy those when reporting bugs. See DEBUG.md.</p>
        </div>
      )}

      {searchInfo && (
        <div className="search-info">
          <p>
            Found <strong>{searchInfo.count}</strong> results
            {searchInfo.query && searchInfo.query !== query && (
              <span className="expanded-terms">
                {' '}• Query: {searchInfo.query}
              </span>
            )}
          </p>
        </div>
      )}

      <ResultsList results={results} loading={loading} />

      {showFilters && (
        <FilterModal
          filters={filters}
          facets={facets}
          onClose={() => setShowFilters(false)}
          onApply={handleFilterChange}
        />
      )}
    </div>
  );
}

export default App;
