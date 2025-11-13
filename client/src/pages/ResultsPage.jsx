import { useLocation, useNavigate } from 'react-router-dom';
import { useState } from "react";
import SearchBar from "../components/SearchBar";
import { searchPapers } from "../services/searchService";

function ResultsPage() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const [results, setResults] = useState(state?.results || []);
  const [isLoading, setLoading] = useState(false);
  const [query, setQuery] = useState(state?.query || "");

  const abstractLen = 200;

  if (!state?.results) {
    // Redirect back if user refreshed or navigated directly
    navigate('/');
    return null;
  }

   const handleSearch = async (newQuery) => {
    setLoading(true);
    try {
      const data = await searchPapers(newQuery);
      setResults(data);
      setQuery(newQuery);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="results-page">
      <SearchBar
        initialQuery={query}
        onSearch={handleSearch}
        isLoading={isLoading}
        horizontal={true}   // <- key prop for horizontal layout
      />

      <div className="results-list">
        {results.length === 0 ? (
          <p className="no-results">No papers found.</p>
        ) : (
          results.map((paper) => (
            <div key={paper.id} className="result-item">
              <a
                href={`https://arxiv.org/pdf/${paper.id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="result-title"
              >
                {paper.title}
              </a>

              <div className="result-authors">
                {paper.authors}
              </div>

              <p className="result-abstract">
                {paper.abstract.length > abstractLen
                  ? paper.abstract.slice(0, abstractLen) + "..."
                  : paper.abstract}
              </p>
            </div>
          ))
        )}
      </div>

      <style>{`
        .results-page {
          max-width: 800px;
          display: flex;
          flex-direction: column;
          align-items: center;
          margin: 2rem auto;
          padding: 0 1rem;
          color: #eaeaea;
          text-align: left;
        }

        .results-header {
          font-size: 1.8rem;
          font-weight: 500;
          margin-bottom: 1.5rem;
        }

        .result-item {
        font-size: 1.2rem;
          margin-bottom: 2rem;
        }

        .result-title {
          color: #8ab4f8;
          font-size: 1.1rem;
          text-decoration: none;
        }

        .result-title:hover {
          text-decoration: underline;
        }

        .result-authors {
          font-size: 0.7rem;
          color: #bbb;
          margin-bottom: 0.3rem;
        }

        .result-abstract {
          font-size: 0.8rem;
          line-height: 1.4;
          color: #ccc;
        }

        .no-results {
          color: #aaa;
          text-align: center;
          margin-top: 2rem;
        }
      `}</style>
    </div>
  );
}

export default ResultsPage;
