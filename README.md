# A2A Content Assistant

A production-grade **multi-agent RAG system** using Google's A2A (Agent-to-Agent) protocol.
Search agent retrieves relevant content from in-house documents using Vertex AI embeddings + ChromaDB.
Main agent synthesizes answers using Gemini Flash.

## Architecture

```
User (Browser/API)
      │
      ▼
┌─────────────────────────┐
│   Main Agent  :8000     │  FastAPI — /chat, /query
│   (Orchestrator)        │  Gemini Flash (LLM synthesis)
└──────────┬──────────────┘
           │  A2A Protocol (HTTP)
           ▼
┌─────────────────────────┐
│  Content Search Agent   │  FastAPI — /.well-known/agent.json, /tasks
│  :8001                  │  ChromaDB + text-embedding-004
└─────────────────────────┘
           │
           ▼
┌─────────────────────────┐
│   ChromaDB Vector Store │  data/embeddings/
│   In-house Documents    │  data/raw/ → data/processed/
└─────────────────────────┘
```

## Quick Start (Day 1)

```bash
git clone <repo>
cd a2a-content-assistant
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set GCP_PROJECT_ID

make run
# → http://localhost:8000/docs
# → GET /api/v1/health  {"status": "ok"}

make test
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI + Uvicorn |
| LLM | Gemini 1.5 Flash (Vertex AI) |
| Embeddings | text-embedding-004 (Vertex AI) |
| Vector Store | ChromaDB |
| Agent Protocol | Google A2A |
| Config | Pydantic Settings |
| Logging | Structlog |
| Testing | Pytest + pytest-asyncio |
| Container | Docker + Compose |

## Project Structure

```
a2a-content-assistant/
├── app/                    # Main Agent FastAPI app
│   ├── main.py             # Entry point (port 8000)
│   ├── api/routes.py       # /health, /chat, /query
│   ├── core/               # Config + logging
│   └── middleware/         # Error handling (Day 6)
├── search_agent_app/       # Content Search Agent (port 8001)
│   ├── main.py             # A2A server entry
│   └── routes.py           # /.well-known/agent.json, /tasks
├── src/
│   ├── a2a/                # A2A protocol schemas + client
│   ├── agents/             # Main agent + search agent logic
│   ├── chains/             # In-process RAG pipeline
│   ├── retrieval/          # Chunking, embeddings, ChromaDB
│   ├── prompts/            # Prompt template manager
│   ├── tools/              # LangChain tools
│   ├── guardrails/         # Input/output safety (Day 6)
│   └── utils/              # LLM client, helpers
├── scripts/                # ingest.py, seed_vectorstore.py
├── eval/                   # Metrics, test cases, eval runner
├── tests/                  # pytest test suite
├── configs/                # config.yaml, prompts.yaml
├── docker/                 # Dockerfile, docker-compose.yaml
└── notebooks/              # Exploration + evaluation notebooks
```

[![CI](https://github.com/DeepeshKashyup/a2a-ai-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/DeepeshKashyup/a2a-ai-assistant/actions/workflows/ci.yml)
