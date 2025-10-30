# Semantic Web Search Engine

A cloud-deployed, serverless-ready semantic search engine that crawls websites, processes HTML into chunks, computes vector embeddings, and performs semantic search over large corpora. Built to showcase modern data engineering, NLP, and scalable architecture skills.

---

## Table of Contents

- [Features](#features)  
- [Architecture](#architecture)  
- [Tech Stack](#tech-stack)  
- [Setup](#setup)  
- [Usage](#usage)  
- [Configuration](#configuration)  
- [License](#license)  

---

## Features

- **Web Crawling:** Recursively crawls websites with configurable depth and seed URLs.  
- **HTML Processing:** Cleans HTML by removing scripts/styles and normalizing whitespace.  
- **Chunking:** Splits long pages into overlapping text chunks for embedding.  
- **Vector Embeddings:** Uses OpenAI or Sentence Transformers for semantic embeddings.  
- **Message Queue:** Kafka-based architecture to decouple crawling, chunking, and embedding.  
- **Database:** PostgreSQL stores page metadata and chunk data.  
- **Vector Database:** Qdrant performs fast similarity search over embeddings.  
- **Serverless Cloud Deployment:** Client and search API hosted on AWS Lambda and S3 for scalable, low-maintenance operation.

---

## Architecture

```
[Web Crawler] --> [PostgreSQL: pages] --> Kafka --> [Chunker Service] --> PostgreSQL: chunks --> Kafka --> [Embedding Service] --> Qdrant
                                            ^
                                            |
                                   HTML cleaned + chunked
```
- **Crawler**: Fetches web pages and stores them in PostgreSQL, sending page IDs to Kafka.  
- **Chunker**: Consumes page IDs, splits pages into chunks, stores them in PostgreSQL, and sends chunk IDs to Kafka.  
- **Embedding Service**: Converts chunks into vector embeddings and stores them in Qdrant for search.  
- **Client**: Web interface queries vector DB for semantic search results, hosted serverlessly on AWS.

---

## Tech Stack

- **Language**: Python 3.11  
- **Web Crawling**: `requests`, `BeautifulSoup`  
- **Text Chunking**: `langchain` `RecursiveCharacterTextSplitter`  
- **Vector Embeddings**: OpenAI `text-embedding-3-small` or HuggingFace `all-mpnet-base-v2`  
- **Databases**: PostgreSQL for pages & chunks, Qdrant for embeddings  
- **Message Queue**: Kafka for event-driven architecture  
- **Deployment**: AWS Lambda, S3, EC2 optional  

---

## Setup

1. Clone the repository:

git clone https://github.com/yourusername/semantic-search-engine.git
cd semantic-search-engine

2. Install dependencies:

pip install -r requirements.txt

3. Configure environment variables (for sensitive info):

export DB_USER=postgres
export DB_PASSWORD=yourpassword
export OPENAI_API_KEY=your_api_key

4. Edit `config.yaml` to set crawler seeds, Kafka topics, and chunking parameters.

---

## Usage

### Running the crawler

python main.py --service crawler

### Running the chunker

python main.py --service chunker

### Running the embedding service

python main.py --service embedder

### Querying the search API

- Access the client hosted on S3 or via serverless API Gateway  
- Enter a search query to get semantically ranked results from Qdrant

---

## Configuration

Example `config.yaml` snippet:

crawler:
  seed_urls:
    - "https://example.com"
  max_pages: 100

database:
  host: "localhost"
  port: 5432
  name: "semantic_search"
  user: "${DB_USER}"
  password: "${DB_PASSWORD}"

kafka:
  bootstrap_servers: "localhost:9092"
  group_id: "chunker_group"
  topic_pages_to_chunk: "pages_to_chunk"
  topic_chunks_to_embed: "chunks_to_embed"
  enable_auto_commit: true
  auto_offset_reset: "earliest"

chunk:
  chunk_size: 500
  overlap: 50
  strip_scripts: true
  clean_whitespace: true
  include_metadata: true

---

## License

MIT License – feel free to use and modify for personal projects or portfolio purposes.
