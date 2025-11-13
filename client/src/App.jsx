import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import SearchBar from "./components/SearchBar";  
import { searchPapers } from './services/searchService';

function App() {
  const [isLoading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async (query) => {
    setLoading(true);
    try {
      const data = await searchPapers(query);
      navigate('/results', { state: { results: data, query } });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Paperfind</h1>
      <SearchBar onSearch={handleSearch} isLoading={isLoading} />
    </div>
  );
}

export default App;
