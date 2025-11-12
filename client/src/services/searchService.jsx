const API_URL = import.meta.env.VITE_API_URL;

/**
 * Perform a search query against the API.
 * @param {string} query - The search term
 * @returns {Promise<any>} - The search results from API
 */
export async function searchPapers(query) {
  if (!query) return [];

  try {
    const response = await fetch(`${API_URL}search?query=${encodeURIComponent(query)}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching search results:", error);
    return [];
  }
}
