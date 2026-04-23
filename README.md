# Mini RAG - Retrieval-Augmented Generation

A lightweight FastAPI application for document-based Q&A using semantic search and LLM generation.

**License**: Apache 2.0 | **Version**: 0.1 | **Python**: 3.10+

## Table of Contents
1. [Features](#features)
2. [Quick Start](#quick-start)
3. [Setup](#setup)
4. [API](#api)
5. [Config](#config)

---

## Features

- 📄 **Document Upload**: TXT and PDF file support
- 🔍 **Semantic Search**: Vector-based document retrieval
- 🤖 **RAG Answers**: AI-powered question answering
- 🔄 **Multi-LLM**: OpenAI or Cohere support
- 🗄️ **Multi-Backend**: PostgreSQL+PGVector or Qdrant
- 🌍 **Multi-language**: English & Arabic
- ⚡ **Async**: Full async/await support
- 📊 **Monitoring**: Prometheus metrics & Grafana dashboards

---

## Quick Start

### 1. Local Development

```bash
# Clone & setup
git clone git@github.com:ahmedmgelwan/mini_rag.git
cd mini_rag
python3 -m venv venv && source venv/bin/activate
pip install -r src/requirements.txt

# Configure
cp src/.env.example src/.env
nano src/.env  # Add API keys

# Database
docker run --name pgvector -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 pgvector/pgvector:0.8.0-pg17 &

cd src && alembic upgrade head

# Run
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs

### 2. Docker Setup

```bash
cd docker
cp env/.env.app.example env/.env.app
nano env/.env.app  # Add API keys

docker-compose up -d
```

Services available at:
- API: http://localhost
- Docs: http://localhost:8000/docs
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

---

## Setup

### Requirements

- Python 3.10+
- PostgreSQL 17 (or use Docker)
- Docker & Docker Compose (for containerized setup)
- OpenAI or Cohere API key

### Environment File (.env)

```env
# App
APP_NAME=Mini RAG APP
APP_VERSION=0.1

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_MAIN_DB=mini_rag_db

# LLM (openai or cohere)
GENERATION_BACKEND=openai
EMBEDDING_BACKEND=openai
GENERATION_MODEL_ID=gpt-3.5-turbo
EMBEDDING_MODEL_ID=text-embedding-ada-002
EMBEDDING_MODEL_SIZE=1536
OPENAI_API_KEY=your_key_here

# Vector DB (PGVECTOR or QDRANT)
VECTOR_DB_BACKEND=PGVECTOR
VECTOR_DB_DISTANCE_METHOD=cosine

# Files
FILE_UPLOADED_MAXIMUM_SIZE=10
FILE_DEFUALT_CHUNK_SIZE=1024

# Generation
GENERATION_DAFAULT_MAX_TOKENS=200
GENERATION_DAFAULT_TEMPERATURE=0.1

# Language (en or ar)
PRIMARY_LANG=en
DEFAULT_LANG=en
```

---

## API

All endpoints return a `signal` field for status and `200` or `400` HTTP codes.

### 1. Upload Document
```http
POST /api/v1/upload/{project_id}
Content-Type: multipart/form-data

file: <binary>
```

**Response:**
```json
{
  "signal": "file_uploaded_success",
  "file_id": "filename_uuid",
  "project_id": "project_uuid"
}
```

---

### 2. Process Documents
```http
POST /api/v1/process/{project_id}
Content-Type: application/json

{
  "file_id": "optional",
  "chunk_size": 100,
  "overlap_size": 20,
  "do_reset": 0
}
```

**Response:**
```json
{
  "signal": "file_processing_success",
  "no_inseted_chunks": 45,
  "processed_files": 2
}
```

---

### 3. Index to Vector DB
```http
POST /api/v1/push/{project_id}

{
  "do_reset": 0
}
```

**Response:**
```json
{
  "signal": "insert_into_vectordb_success",
  "inserted_items_count": 45
}
```

---

### 4. Get Collection Info
```http
GET /api/v1/info/{project_id}
```

**Response:**
```json
{
  "signal": "collection_info_reteived",
  "collection_info": {
    "project_id": "uuid",
    "total_chunks": 120,
    "indexed_chunks": 115
  }
}
```

---

### 5. Search
```http
POST /api/v1/search/{project_id}

{
  "text": "What is machine learning?",
  "limit": 5
}
```

**Response:**
```json
{
  "signal": "vector_db_search_success",
  "results": [
    {
      "chunk_id": "uuid",
      "chunk_text": "...",
      "similarity_score": 0.95
    }
  ]
}
```

---

### 6. Answer (RAG)
```http
POST /api/v1/answer/{project_id}

{
  "text": "What is machine learning?",
  "limit": 5
}
```

**Response:**
```json
{
  "signal": "rag_answer_success",
  "answer": "Machine learning is...",
  "full_prompt": "...",
  "chat_history": [...]
}
```

---

## Config

### LLM Providers

**OpenAI:**
```env
GENERATION_BACKEND=openai
EMBEDDING_BACKEND=openai
GENERATION_MODEL_ID=gpt-3.5-turbo
EMBEDDING_MODEL_ID=text-embedding-ada-002
EMBEDDING_MODEL_SIZE=1536
OPENAI_API_KEY=sk-...
```

**Cohere:**
```env
GENERATION_BACKEND=cohere
EMBEDDING_BACKEND=cohere
GENERATION_MODEL_ID=command
EMBEDDING_MODEL_ID=embed-english-v3.0
EMBEDDING_MODEL_SIZE=1024
COHERE_API_KEY=...
```

### Vector Databases

**PGVector (recommended for small-medium):**
```env
VECTOR_DB_BACKEND=PGVECTOR
VECTOR_DB_DISTANCE_METHOD=cosine
VECTOR_DB_PGVEC_INDEX_THRESHOLD=1000
```

**Qdrant (recommended for large scale):**
```env
VECTOR_DB_BACKEND=QDRANT
VECTOR_DB_PATH=./qdrant_data
VECTOR_DB_DISTANCE_METHOD=cosine
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI 0.110+ |
| **Server** | Uvicorn |
| **Database** | PostgreSQL 17 |
| **Vector** | PGVector or Qdrant |
| **ORM** | SQLAlchemy 2.0 |
| **LLM** | OpenAI / Cohere |
| **Monitoring** | Prometheus / Grafana |
| **Container** | Docker / Compose |

---

## Project Structure

```
src/
├── main.py                # FastAPI app
├── controllers/           # Business logic
├── routes/               # API endpoints
├── models/               # Database models
├── stores/               # LLM & Vector DB clients
├── helpers/              # Configuration
└── utils/                # Metrics
```

---

## Common Commands

```bash
# Local development
cd src
uvicorn main:app --reload

# Docker
cd docker
docker-compose up -d
docker-compose logs -f fastapi
docker-compose down

# Database migrations
cd src
alembic upgrade head
alembic downgrade -1

# API documentation
# Browser: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

---

## Troubleshooting

### PostgreSQL Connection Error
```bash
# Check if postgres is running
docker ps | grep pgvector

# Test connection
psql -h localhost -U postgres -d mini_rag_db
```

### API Key Invalid
```bash
# Verify your key
echo $OPENAI_API_KEY

# Update .env
nano src/.env

# Restart app
pkill -f uvicorn
cd src && uvicorn main:app --reload
```

### Docker Issues
```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose up --build

# Reset everything
docker-compose down -v
docker-compose up
```

---

## License

Apache 2.0
