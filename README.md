# Mini RAG - Retrieval-Augmented Generation

A lightweight FastAPI application for document-based Q&A using semantic search and LLM generation.

## Features

- **Document Management**: Upload and process files into semantic chunks
- **Semantic Search**: Find relevant documents using vector embeddings
- **RAG Answers**: Generate AI responses based on retrieved documents
- **Multi-LLM Support**: OpenAI or Cohere for embeddings & generation
- **Multi-language**: English & Arabic prompts
- **Vector DB**: Qdrant for semantic storage
- **Batch Embeddings**: Optimized API calls (N chunks = 1 embedding request)

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

## Run

```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Data Management
- `POST /api/v1/upload/{project_id}` - Upload file to project
- `POST /api/v1/process/{project_id}` - Split file into chunks

### Vector Database
- `POST /api/v1/push/{project_id}` - Index chunks to vector DB
- `GET /api/v1/info/{project_id}` - Get collection stats

### RAG Operations
- `POST /api/v1/search/{project_id}` - Search documents (semantic)
- `POST /api/v1/answer/{project_id}` - Get AI answer with sources

## Configuration

Key environment variables in `.env`:
- `GENERATION_BACKEND` - `openai` or `cohere`
- `EMBEDDING_BACKEND` - LLM provider for embeddings
- `VECTOR_DB_BACKEND` - Vector database type
- `PRIMARY_LANG` - Language for prompts (`en` or `ar`)
- MongoDB, API keys, model IDs, etc.

## Architecture

```
Upload File → Process Chunks → Generate Embeddings → Index to Vector DB
                                      ↓
                              User Query → Search Vectors → Retrieve Docs
                                                                 ↓
                                             Combine with Prompt Template → LLM → Answer
```

## Tech Stack

- **Framework**: FastAPI, Uvicorn
- **Database**: MongoDB (Motor async)
- **Vector Store**: Qdrant
- **LLM**: OpenAI / Cohere APIs
- **Runtime**: Python 3.9+
