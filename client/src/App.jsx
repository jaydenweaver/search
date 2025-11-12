import { useState } from 'react';
import { searchPapers } from './services/searchService';

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = await searchPapers(query);
    setResults(data);
    console.log(data);
  }

  return (
    <div className="container">
      
      <h1 className="">Paperfind</h1>

      <form 
        onSubmit={handleSubmit} 
        className="search-form"
      >
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search papers..."
        />

        <button
          type="submit"
        >
          Search
        </button>
      </form>

    </div>
  )
}

export default App;
