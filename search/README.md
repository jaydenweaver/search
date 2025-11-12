# Paperfind API

Paperfind API is a FastAPI search service for academic papers. It generates embeddings for user queries using OpenAI, searches a Qdrant vector database for relevant papers, and fetches metadata from Supabase. The API is designed with robust error handling, retries, and rate-limit handling.

---

## Features

- Semantic search over academic papers using OpenAI embeddings.
- Stores and queries vectors with Qdrant.
- Fetches paper metadata from Supabase.
- Structured exception handling with custom error classes:
  - `ExternalServiceError` for downstream failures.
  - `RateLimitExceeded` for OpenAI rate limiting.
  - `NotFoundError` for empty search results.
- Retry logic with exponential backoff and jitter for transient errors.
- CORS configured for frontend access.

---

## Requirements

- Python 3.11+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/) for ASGI server
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Qdrant Client](https://github.com/qdrant/qdrant_client)
- [Supabase Python Client](https://supabase.com/docs/reference/python)
- `python-dotenv` and `PyYAML` for configuration

---

## Installation

1. **Clone the repository**

```
git clone <repository_url>
cd search
```

2. **Create a virtual environment**

```
python -m venv venv
source venv/bin/activate      # linux / macOS
venv\Scripts\activate         # windows
```

3. **Install dependencies**

```
pip install -r requirements.txt
```

4. **Create `.env` file** in the project root with:

```
OPENAI_API_KEY=<your_openai_api_key>
QDRANT_URL=<your_qdrant_url>
QDRANT_API_KEY=<your_qdrant_api_key>
SUPABASE_URL=<your_supabase_url>
SUPABASE_SERVICE_KEY=<your_supabase_service_key>
```

5. **Edit `config.yaml`** to configure:

```
openai:
  model: text-embedding-3-small

qdrant:
  collection_name: papers

max_retries: 3
base_delay: 0.5
supabase:
  papers_table: papers
```

---

## Running the Server

Start the FastAPI server using Uvicorn:

```
uvicorn main:app --reload
```

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API Endpoints

### `GET /search`

Search for papers by query.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query`  | string | Search query (min 3 characters) |

**Response:**

```
[
  {
    "id": "paper123",
    "title": "Example Paper Title",
    "authors": "Author A, Author B",
    "abstract": "Paper abstract...",
    "score": 0.923
  }
]
```

**Errors:**

| Status Code | Error Class | Description |
|-------------|------------|-------------|
| 404         | `NotFoundError` | No papers found for the query |
| 429         | `RateLimitExceeded` | OpenAI rate limit reached |
| 502         | `ExternalServiceError` | Downstream service unavailable |

---

## Exception Handling

All exceptions inherit from `AppError`:

- **ExternalServiceError** – Qdrant, Supabase, or OpenAI failures.  
- **RateLimitExceeded** – Raised on OpenAI rate limit errors.  
- **NotFoundError** – No papers found for a query.  

Global exception handlers automatically return JSON responses with structured error information.

---

## Development Tips

- `--reload` in Uvicorn enables hot reload for development.
- Use environment variables for sensitive keys.
- Configure logging to replace `print()` statements for better traceability in production.

---

## License

MIT License © 2025 Jayden
