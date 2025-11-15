# Paperfind.io

This repository contains the full codebase for **Paperfind.io**, a cloud-native semantic search engine for academic literature.  
It is structured as a **modular monorepo**, with each major component isolated into its own directory.

Paperfind.io provides fast, meaning-aware retrieval of research papers using vector embeddings, indexing, Qdrant similarity search, and a modern React frontend.

---

## Repository Structure

```
/
├── embedding/ 	# data ingestion module: JSONL parsing, metadata extraction, embedding, Qdrant + PostgreSQL upload
├── lambda_search/ 	# AWS Lambda search function
├── search/ 	# FastAPI search server (can replace lambda for local/dev/self-hosted)
└── client/		# React (Vite) frontend for querying and visualizing results
```

---

## Modules Overview

### **1. Data Ingestion Module (`embedding/`)**
Handles the end-to-end process of preparing academic papers for semantic search:
- JSONL extraction (id, title, authors, abstract, categories)
- Embedding generation using OpenAI
- Uploading chunks + metadata to Qdrant / PostgreSQL

This module is designed to run offline as a batch pipeline.

---

### **2. Lambda Search Function (`lambda_search/`)**
A lightweight search function intended for **AWS Lambda + API Gateway**.  
Implements the full semantic search flow:
- Query embedding  
- Vector similarity search (Qdrant)  
- Results aggregation with Qdrant vectors + PostgreSQL metadata

Primarily suited for serverless deployments.

---

### **3. FastAPI Search Server (`search/`)**
A fully async FastAPI search server with nearly identical functionality to the Lambda function.  
Useful for:
- Local development  
- Self-hosted / server deployments  

Drop-in replacement for the lambda module.

---

### **4. React Frontend (`client/`)**
A fast UI for academic semantic search.

Features:
- Input-based semantic search  
- Responsive, minimal UI design  

Runs against either the FastAPI server or the Lambda endpoint.

---

## High-Level Search Architecture

1. User submits a query  
2. System generates query embeddings  
3. Qdrant retrieves top-k similar embeddings
4. Embedding + metadata is aggregated into full results
6. Frontend displays the ranked papers  

---

## License

MIT License - open and free for personal or commercial use.


