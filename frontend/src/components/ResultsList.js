import React from 'react';

function ResultsList({ results, loading }) {
  if (loading) {
    return (
      <div className="results-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Searching papers...</p>
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return null;
  }

  return (
    <div className="results-container">
      {results.map((paper) => (
        <div key={paper.paper_id} className="result-card">
          <div className="result-header">
            <h3 className="result-title">{paper.title}</h3>
            <div className="result-meta">
              <span className="badge category">{paper.primary_category}</span>
              <span className="date">{paper.published}</span>
              {paper.score && (
                <span className="score">Score: {paper.score.toFixed(2)}</span>
              )}
            </div>
          </div>

          <p className="result-authors">
            <strong>Authors:</strong> {paper.authors}
          </p>

          <p className="result-abstract">
            {paper.abstract.length > 300
              ? `${paper.abstract.substring(0, 300)}...`
              : paper.abstract}
          </p>

          <div className="result-actions">
            <a
              href={paper.pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              className="action-btn download"
              download
            >
              📄 Download PDF
            </a>
            <a
              href={paper.url}
              target="_blank"
              rel="noopener noreferrer"
              className="action-btn view"
            >
              🔗 View on arXiv
            </a>
          </div>

          {paper.categories && (
            <div className="result-categories">
              <strong>Categories:</strong>{' '}
              {paper.categories.split(', ').map((cat, idx) => (
                <span key={idx} className="category-tag">
                  {cat}
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default ResultsList;
