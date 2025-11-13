import { useState } from 'react';
import { searchPapers } from './services/searchService';

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [isLoading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await searchPapers(query);
      setResults(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Paperfind</h1>

      <form onSubmit={handleSubmit} className="search-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search papers..."
        />

        <button type="submit" disabled={isLoading}>
          <span className={`fade-text ${isLoading ? 'fade-out' : 'fade-in'}`}>Search</span>
          <div className={`spinner ${isLoading ? 'fade-in-delayed' : 'fade-out'}`} />
        </button>
      </form>

      <style>{`
        .search-form button {
          position: relative;
          border: 1px solid #333;
          border-radius: 9999px;
          padding: 0.6em 1.2em;
          font-size: 1em;
          font-weight: 500;
          font-family: inherit;
          background-color: #1a1a1a;
          cursor: pointer;
          transition: border-color 0.25s;
          min-width: 98px;
          min-height: 43px;
          color: white;
          overflow: hidden;
        }

        .search-form button:hover:not(:disabled) {
          border-color: #ffffff;
        }

        .search-form button:disabled {
          border-color: #333;
          cursor: not-allowed;
        }

        .fade-text,
        .spinner {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        .fade-in {
          opacity: 1;
          transition-delay: 0s;
        }

        .fade-in-delayed {
          opacity: 1;
          transition-delay: 0.3s; /* starts after text fade-out ends */
        }

        .fade-out {
          opacity: 0;
          transition-delay: 0s;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid rgba(255, 255, 255, 0.5);
          border-top-color: white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: translate(-50%, -50%) rotate(0deg); }
          100% { transform: translate(-50%, -50%) rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default App;
