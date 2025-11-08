# Academic Paper Embedding Module

This project provides a robust pipeline to process academic papers from arXiv, generate vector embeddings from their abstracts, and store the results in a vector database (Qdrant) with metadata in Supabase. The pipeline supports **large datasets**, **streaming**, **batching**, **checkpointing**, and **rate-limited async processing**.

---

## Features

- ```Streaming ingestion```: Processes large JSON datasets line by line to avoid memory issues.  
- ```Batch embedding```: Generates embeddings in batches using OpenAI embeddings API.  
- ```Metadata storage```: Saves paper metadata in Supabase for easy querying.  
- ```Vector storage```: Stores embeddings in Qdrant for semantic search.  
- ```Filtering```: Supports filtering by category (e.g., `cs.LG`) and publication year.  
- ```Checkpointing```: Resumes long-running processes from the last processed paper.  
- ```Async processing with backoff```: Retries API calls with exponential backoff and jitter on rate limits or timeouts.  
- ```Thread-safe sync execution```: Synchronous functions run asynchronously using `asyncio.to_thread()` for better concurrency.  

---

## Project Structure

```
embedding/
│
├─ main.py                 # Entry point to run the pipeline
├─ config.yaml             # Configuration file
├─ requirements.txt        # Python dependencies
├─ .env                    # Environment variables (API keys, URLs)
├─ data/
│   └─ dataset.jsonl       # JSONL dataset of papers
└─ src/
   ├─ __init__.py
   ├─ process.py           # Main pipeline logic
   ├─ embedding.py         # Embedding helper functions
   ├─ vector.py            # Qdrant vector storage functions
   ├─ db.py                # Supabase metadata storage
   └─ checkpoint.py        # Checkpoint saving/loading
```

---

## Installation

1. **Clone the repository**
```
git clone git@github.com:jaydenweaver/search.git        # ssh
# or
git clone https://github.com/jaydenweaver/search.git    # https

cd search/embedding
```

2. **Create a virtual environment**
```
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
# or
source venv/bin/activate      # macOS/Linux
```

3. **Install dependencies**
```
pip install -r requirements.txt
```

4. **Set up environment variables**  
Create a `.env` file in the root directory with your API keys and URLs:

```
SUPABASE_URL=<your_supabase_url>
SUPABASE_SERVICE_KEY=<your_supabase_service_key>
OPENAI_API_KEY=<your_openai_api_key>
QDRANT_URL=<your_qdrant_url>
QDRANT_API_KEY=<your_qdrant_api_key>
```

5. **Configure `config.yaml`**  

Your configuration file should include dataset paths, API models, batch size, and retry/backoff settings. Example:

```
openai:
  model: "text-embedding-3-small"
  batch_size: 100
  sleep_between_batches: 1

supabase:
  papers_table: "papers"

qdrant:
  collection_name: "papers"
  vector_size: 1536
  initial_sleep: 30
  
dataset:
  path: "data/arxiv-metadata-oai-snapshot.json"
  id_field: "id"
  abstract_field: "abstract"
  authors_field: "authors_parsed"
  categories_field: "categories"
  from_year: 2023
  checkpoint_path: checkpoint.txt

logging:
  level: "INFO"
  log_file: "batch_embedding.log"

advanced:
  max_retries: 5
  base_delay: 2.0
  max_workers: 4
```

---

## Usage

1. **Run the pipeline**
```
python main.py
```

2. **Pipeline workflow**  
   - Streams the JSONL dataset line by line.  
   - Filters papers by category (`cs.LG`) and year (`from_year` in `config.yaml`).  
   - Generates embeddings for abstracts using OpenAI API with **async backoff** for rate limiting.  
   - Stores metadata in Supabase.  
   - Stores embeddings in Qdrant.  
   - Saves progress via **checkpointing**, allowing resuming if interrupted.  

3. **Checkpointing**  
   - The pipeline writes the last processed paper ID to a checkpoint file.  
   - On restart, it resumes from the last checkpoint automatically.  

4. **Rate-limiting**  
   - The pipeline respects OpenAI API limits using `sleep_between_batches` and exponential backoff with jitter.  

---

## Notes

- Adjust `batch_size` and `sleep_between_batches` in `config.yaml` to stay within OpenAI API rate limits.  
- Only papers matching the specified category and year are processed.  
- Async-safe execution ensures synchronous functions do not block the event loop.  

---

## Dependencies

- Python 3.13  
- PyYAML  
- python-dotenv  
- openai  
- qdrant-client  
- supabase  
- tenacity  

---

## License

This project is licensed under the MIT License.
