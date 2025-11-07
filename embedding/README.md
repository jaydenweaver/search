# Academic Paper Embedding Module

This project provides a pipeline to process academic papers from arXiv, generate vector embeddings from their abstracts, and store the results in a vector database (Qdrant) with metadata in Supabase. The pipeline is designed to handle large datasets efficiently with streaming, batching, and checkpointing support.

---

## Features

- ```Streaming ingestion```: Processes large JSON datasets line by line to avoid memory issues.
- ```Batch embedding```: Uses OpenAI embeddings API to vectorize abstracts in batches.
- ```Metadata storage```: Stores paper metadata in Supabase for easy querying.
- ```Vector storage```: Stores embeddings in Qdrant for semantic search.
- ```Filtering```: Supports filtering by categories (e.g., `cs.LG`) and publication year.
- ```Checkpointing```: Supports resuming long-running processes from the last processed paper.

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
git clone <repo_url>
cd embedding
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
Set dataset paths, batch sizes, and other options. Example:

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
  retry_attempts: 3
  max_parallel_requests: 5
```

---

## Usage

1. **Run the pipeline**
```
python main.py
```

2. **Pipeline workflow**
   - Streams JSON dataset line by line.
   - Filter papers by category (`cs.LG`) and year (`from_year` in `config.yaml`).
   - Generate embeddings for abstracts using OpenAI API.
   - Store metadata in Supabase.
   - Store embeddings in Qdrant.

3. **Checkpointing**  
   - The pipeline supports checkpointing for long runs. If interrupted, it resumes from the last processed paper.

---

## Notes

- Adjust ```batch_size``` and ```sleep_between_batches``` to stay within OpenAI API rate limits.
- Only papers in the specified category and after the specified year are processed.

---

## Dependencies

- Python 3.8+ (recommended 3.10+ for modern type hints)
- PyYAML
- python-dotenv
- openai
- qdrant-client
- supabase
- tenacity

---

## License

This project is licensed under the MIT License.
