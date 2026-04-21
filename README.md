# Mini RAG - Retrieval-Augmented Generation

Lightweight FastAPI application for document-based Q&A using semantic search and LLM generation.

## Features

- **Document Management**: Upload and process files into semantic chunks
- **Semantic Search**: Find relevant documents using vector embeddings
- **RAG Answers**: Generate AI responses based on retrieved documents
- **Multi-LLM Support**: OpenAI or Cohere for embeddings & generation
- **Multi-Vector DB**: PostgreSQL+PGVector or Qdrant
- **Multi-language**: English & Arabic prompts
- **Async**: Full async/await support with SQLAlchemy

## Setup

```bash
pip install -r src/requirements.txt
cp src/.env.example src/.env
```

## Run

```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

**Database**
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USERNAME`, `POSTGRES_PASSWORD`, `POSTGRES_MAIN_DB`
- `VECTOR_DB_BACKEND` - `PGVECTOR` or `QDRANT`
- `VECTOR_DB_PATH` - Path for Qdrant (local)

**LLM & Embeddings**
- `GENERATION_BACKEND`, `EMBEDDING_BACKEND` - `openai` or `cohere`
- `GENERATION_MODEL_ID`, `EMBEDDING_MODEL_ID`, `EMBEDDING_MODEL_SIZE`
- `OPENAI_API_KEY`, `COHERE_API_KEY`

**File Processing**
- `FILE_DEFUALT_CHUNK_SIZE` - Chunk size in characters
- `INPUT_DAFAULT_MAX_CHARACTERS` - Max input length
- `GENERATION_DAFAULT_MAX_TOKENS`, `GENERATION_DAFAULT_TEMPERATURE`

**Localization**
- `PRIMARY_LANG`, `DEFAULT_LANG` - `en` or `ar`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/upload/{project_id}` | Upload file |
| `POST` | `/api/v1/process/{project_id}` | Process file into chunks |
| `POST` | `/api/v1/push/{project_id}` | Index chunks to vector DB |
| `GET` | `/api/v1/info/{project_id}` | Get collection info |
| `POST` | `/api/v1/search/{project_id}` | Search documents |
| `POST` | `/api/v1/answer/{project_id}` | Get AI answer |

## Tech Stack

- **Framework**: FastAPI, Uvicorn
- **Database**: PostgreSQL (async with asyncpg)
- **Vector Store**: PGVector / Qdrant
- **ORM**: SQLAlchemy 2.0 (async)
- **LLM**: OpenAI / Cohere
- **Python**: 3.9+
