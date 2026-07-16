# Local RAG Chatbot

A secure, full-stack, entirely local AI enterprise architecture featuring user authentication, protected chat histories, NVIDIA safety guardrails, deep document intelligence, and a pluggable autonomous agent.

## Core Features
* **🔐 User Authentication:** Secure signup and login flow powered by JWT tokens, managing private sessions per user.
* **📜 Persistent Chat History:** SQLite-backed SQL database logging historical chat interaction threads across sessions.
* **🛡️ NVIDIA NeMo Guardrails:** Advanced topical, safety, and security guardrail configurations managing input/output moderation boundaries.
* **📂 Multi-Format RAG Ingestion:** Industrial loaders digesting PDF, Excel, HTML, and raw Text files into a local ChromaDB vector store.
* **🤖 Autonomous MCP Agent:** A LangGraph React Agent linked to a custom FastMCP server carrying out web-scraping and real-time environment actions.

Everything runs locally on your machine — zero external API dependency, absolute data privacy.

---

## Workspace Architecture

```text
vignatrix-ragone/
├── backend/                    FastAPI + SQLAlchemy Core + LangChain + Ollama
│   ├── guardrails_config/      NVIDIA NeMo Guardrails safety policies and rails configuration files
│   ├── rag/                    Retrieval workflows (loaders, vector store, generation chain)
│   ├── routers/                Modular API endpoints (auth, chat, documents routing)
│   ├── auth.py                 JWT tokens handling, hashing, and security middleware
│   ├── database.py             SQLAlchemy DB instance & session manager
│   ├── models.py               Database tables definitions (Users, Chat History logs)
│   ├── schemas.py              Pydantic data validation contracts 
│   ├── main.py                 API startup core anchoring routes & lifecycles
│   ├── config.py               Environment properties mapper
│   ├── local_rag.db            Active SQLite database tracking users & chat states (gitignored)
│   └── requirements.txt
├── data/                       Centralized Multi-Format Raw Knowledge base
│   ├── excel/                  Excel datasheets (.xlsx, .xls)
│   ├── html/                   Web page raw DOM files
│   ├── pdf/                    Text/Scan document formats
│   ├── text_files/             Raw layout (.txt) materials
│   └── vector_store/           Persisted local ChromaDB collection directories
├── frontend/                   React (Vite) + Tailwind CSS SPA Client
│   └── src/
│       ├── components/         FileUpload, Chatbox, and Dynamic ChatMessage bubbles
│       ├── App.jsx             Layout orchestration handling Login view vs Dashboard view
│       └── api.js              Centralized HTTP request client carrying Auth Bearer tokens
├── mcp-weather-server/         Autonomous Agent Framework Core
│   ├── app.py                  Gradio Interface hosting the multi-tool Agent app
│   ├── weather.py              FastMCP implementation hosting `get_weather` & `read_website` tools
│   └── test_agent.py           CLI verification script running LangGraph agent tasks
├── docker-compose.yml          Multi-container infrastructure composer
├── start.sh                    Convenience orchestrator spinning up the complete environment
└── README.md                   Project blueprint manual

```

---

## Prerequisites

1. **[Ollama Engine](https://ollama.com)** actively operational locally.
2. Pull the required LLM generation and embedding assets:
```bash
ollama pull gemma4:12b
ollama pull nomic-embed-text

```


3. **Python 3.11+** environment and **Node.js 18+** environment tools.

---

## Quick Launch Environments

### Option A: 🚀 Infrastructure Automation (Docker)

Ensure Docker Desktop is operational on the host system, then execute:

```bash
docker compose up --build -d

```

Access the global user web interface at: **http://localhost:5174**

### Option B: 🛠️ Direct Manual Initialization

#### 1. Backend API & Relational Database

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Tune ports or custom parameters if necessary
uvicorn main:app --reload --port 8000

```

#### 2. Frontend Login & Interface Client

In a second terminal context:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev

```

#### 3. Pluggable MCP Multi-Tool Dashboard

In a third terminal context:

```bash
cd mcp-weather-server
python3 -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install gradio langchain-ollama langchain-mcp-adapters langgraph fastmcp mcp beautifulsoup4 httpx
python app.py

```

Interact visually with the agent via: **http://localhost:7860**

---

## Running Applications Guide

### 1. Main RAG Client Interface (`localhost:5174`)

* **Authentication Portal:** Create a new user profile or log in with verified credentials. The frontend manages session protection via state-stored JWT keys.
* **Data Ingestion:** Route raw tracking assets directly to the ingestion system. The backend analyzes the files, applies safety checkpoints via `guardrails_config` (NVIDIA NeMo configurations), parses text strings, embeds vectors, and locks chunks securely under `data/vector_store`.
* **Contextual Conversations:** Chat queries map dynamically against historical data strings inside `local_rag.db`, pulling relevant fragments into local Ollama prompts to formulate verified citations.

### 2. Autonomous Agent Studio (`localhost:7860`)

* Instruct the agent to perform actions requiring live real-time analysis:
> *"Look at the headline on https://thehackernews.com/ and check if that vulnerability introduces threats today based on Guntur weather or physical factors."*


* The system parses arguments dynamically via the adapter framework, coordinates tool execution through standard I/O pipelines, performs network fetching, parses HTML objects safely, and returns clean results directly to the display window.

---

## Environment Property Management (`backend/.env`)

| Property Key | Default Value | Usage Scope |
| --- | --- | --- |
| `SECRET_KEY` | *Auto-Generated String* | Cryptographic salt initializing security JWT hashes |
| `DATABASE_URL` | `sqlite:///./local_rag.db` | System path anchoring users, tokens, and history schemas |
| `OLLAMA_BASE_URL` | `http://host.docker.internal:11434` | Bridge locator addressing host machine LLM engines from isolated engines |
| `OLLAMA_LLM_MODEL` | `gemma4:12b` | Default logic and text production model asset |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Matrix model encoding tokens into mathematical vectors |

```

```
