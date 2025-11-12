import { useState } from 'react'

function App() {
  const [query, setQuery] = useState("")

  const handleSubmit = (e) => {
    e.preventDefault()
    console.log("Searching for:", query)
    // Call your API here
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

export default App
