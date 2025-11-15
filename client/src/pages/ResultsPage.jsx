import { useLocation, useNavigate } from 'react-router-dom';
import { useState } from "react";
import SearchBar from "../components/SearchBar";
import { searchPapers } from "../services/searchService";
import { Link } from "react-router-dom";


function ResultsPage() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const [results, setResults] = useState(state?.results || []);
  const [isLoading, setLoading] = useState(false);
  const [query, setQuery] = useState(state?.query || "");

  const abstractLen = 200;
  const titleLen = 70;
  const authorsLen = 100;

  if (!state?.results) {
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
    <div>
      <div className="header-bar">
        <Link to="/">
          <h1 className="clickable-title">Paperfind</h1>
        </Link>
        <SearchBar
          initialQuery={query}
          onSearch={handleSearch}
          isLoading={isLoading}
          horizontal={true}
        />
      </div>
      <div className="results-page">
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
                  {paper.title.length > titleLen
                    ? paper.title.slice(0, titleLen) + "..."
                    : paper.title}
                </a>

                <div className="result-authors">
                  {paper.authors.length > authorsLen
                    ? paper.authors.slice(0, authorsLen) + "..."
                    : paper.authors}
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

          @media (max-width: 900px) {
            .results-page,
            .header-bar {
              padding-left: 1.5rem;
              padding-right: 1.5rem;
            }
          }

          @media (max-width: 700px) {
            .header-bar h1 {
              display: none;
            }
          }

          .clickable-title {
            color: #ffffff;
            text-decoration: none;
            cursor: pointer; 
          }

          .header-bar {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
          }
            
          a {
            font-weight: 500;
            color: #646cff;
            text-decoration: inherit;
          }
            
          a:hover {
            color: #535bf2;
          }

          .results-page {
            max-width: 800px;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0rem auto;
            color: #fafafa;
            text-align: left;
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

          @media (prefers-color-scheme: light) {
            .clickable-title {
              color: #000000;
              text-decoration: none;
              cursor: pointer; 
            }

            .no-results {
              color: #000000;
              text-align: center;
              margin-top: 2rem;
            }

            .result-title {
              color: #4d56ffff;
            }

            .result-title:hover {
              color: #2d37ecff;
            }

            .result-abstract {
              color: #000000;
            }

            .result-authors {
              color: #000000b7;
            }
          }
        `}</style>
      </div>
    </div>
    
  );
}

export default ResultsPage;
