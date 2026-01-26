import React from 'react';

function StatsPanel({ stats }) {
  if (!stats) return null;

  return (
    <div className="stats-panel">
      <div className="stat-item">
        <span className="stat-value">{stats.total_papers?.toLocaleString()}</span>
        <span className="stat-label">Total Papers</span>
      </div>
      <div className="stat-item">
        <span className="stat-value">{stats.recent_papers_1yr?.toLocaleString()}</span>
        <span className="stat-label">Recent (1 year)</span>
      </div>
      <div className="stat-item">
        <span className="stat-value">{Object.keys(stats.top_categories || {}).length}</span>
        <span className="stat-label">Categories</span>
      </div>
    </div>
  );
}

export default StatsPanel;
