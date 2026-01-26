import React, { useState } from 'react';

function FilterModal({ filters, facets, onClose, onApply }) {
  const [localFilters, setLocalFilters] = useState(filters);

  const handleChange = (key, value) => {
    setLocalFilters({ ...localFilters, [key]: value });
  };

  const handleApply = () => {
    onApply(localFilters);
    onClose();
  };

  const handleReset = () => {
    const resetFilters = {
      category: '',
      yearFrom: '',
      yearTo: '',
      author: '',
      sort: 'relevance',
      semantic: true,
      limit: 10,
    };
    setLocalFilters(resetFilters);
    onApply(resetFilters);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🔧 Advanced Filters</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          <div className="filter-group">
            <label>Category</label>
            <select
              value={localFilters.category}
              onChange={(e) => handleChange('category', e.target.value)}
            >
              <option value="">All Categories</option>
              {facets?.categories?.slice(0, 20).map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.value} ({cat.count})
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Year Range</label>
            <div className="year-range">
              <input
                type="number"
                placeholder="From"
                value={localFilters.yearFrom}
                onChange={(e) => handleChange('yearFrom', e.target.value)}
                min={facets?.year_range?.min}
                max={facets?.year_range?.max}
              />
              <span>to</span>
              <input
                type="number"
                placeholder="To"
                value={localFilters.yearTo}
                onChange={(e) => handleChange('yearTo', e.target.value)}
                min={facets?.year_range?.min}
                max={facets?.year_range?.max}
              />
            </div>
          </div>

          <div className="filter-group">
            <label>Author</label>
            <input
              type="text"
              placeholder="Author name"
              value={localFilters.author}
              onChange={(e) => handleChange('author', e.target.value)}
            />
          </div>

          <div className="filter-group">
            <label>Sort By</label>
            <select
              value={localFilters.sort}
              onChange={(e) => handleChange('sort', e.target.value)}
            >
              <option value="relevance">Relevance</option>
              <option value="date_desc">Newest First</option>
              <option value="date_asc">Oldest First</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Results Limit</label>
            <input
              type="number"
              value={localFilters.limit}
              onChange={(e) => handleChange('limit', parseInt(e.target.value) || 10)}
              min="1"
              max="100"
            />
          </div>

          <div className="filter-group checkbox">
            <label>
              <input
                type="checkbox"
                checked={localFilters.semantic}
                onChange={(e) => handleChange('semantic', e.target.checked)}
              />
              Enable semantic search (query expansion)
            </label>
          </div>
        </div>

        <div className="modal-footer">
          <button className="reset-btn" onClick={handleReset}>
            Reset All
          </button>
          <button className="apply-btn" onClick={handleApply}>
            Apply Filters
          </button>
        </div>
      </div>
    </div>
  );
}

export default FilterModal;
