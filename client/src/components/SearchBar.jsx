import { useState } from 'react';

function SearchBar({ initialQuery = "", onSearch, isLoading, horizontal = false }) {
  const [query, setQuery] = useState(initialQuery);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSearch(query);
  };

  return (
    <form onSubmit={handleSubmit} className={`search-form ${horizontal ? "horizontal" : ""}`}>
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

        <style>{`

        .search-form.horizontal {
          flex-direction: row;
          justify-content: center;
        }

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
            border-color: #fafafa;
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

        @media (prefers-color-scheme: light) {
            .search-form input{
                border-color: #979797;
                background-color: #fafafa;
            }

            .search-form input:hover,
            .search-form input:focus{ 
                border-color: #000000;
            }

            .search-form button {
                border: 1px solid #979797;
                background-color: #fafafa;
                color: #000000;
            }

            .search-form button:hover:not(:disabled) {
                border-color: #000000;
            }

            .search-form button:disabled {
                border-color: #979797;
            }

            .spinner {
                border: 2px solid #000000;
                border-top-color: #979797;
            }
        }
        `}</style>
    </form>
  );
}
export default SearchBar;