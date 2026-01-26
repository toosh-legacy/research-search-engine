import React from 'react';

function SearchBar({ query, setQuery, onSearch, onOpenFilters, loading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <div className="search-box">
      <form onSubmit={handleSubmit} className="search-input-wrapper">
        <input
          type="text"
          className="search-input"
          placeholder="Search papers... (e.g., 'machine learning', 'neural networks', 'quantum computing')"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading}
        />
        <button
          type="button"
          className="filters-btn"
          onClick={onOpenFilters}
        >
          ⚙️ Filters
        </button>
        <button
          type="submit"
          className="search-btn"
          disabled={loading || !query.trim()}
        >
          {loading ? '⏳ Searching...' : '🔍 Search'}
        </button>
      </form>
    </div>
  );
}

export default SearchBar;
