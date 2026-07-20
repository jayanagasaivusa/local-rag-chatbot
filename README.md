# Local RAG & Data Intelligence Platform

A secure, full-stack, local AI enterprise architecture featuring user authentication, protected chat histories, NVIDIA safety guardrails, and a **Dual-Engine AI** (Multimodal Vector Intelligence + Autonomous Pandas Data Analyst).

## Core Features

* **🔐 User Authentication:** Secure signup/login via JWT tokens with session-isolated chat history.
* **🛡️ NVIDIA NeMo Guardrails:** Advanced topical, safety, and security guardrail configurations.
* **🧠 Dual-Engine AI Architecture:**
    * **Engine 1 (Unstructured RAG):** Premium hybrid-search pipeline using **PostgreSQL + pgvector**, **BM25**, and **Cross-Encoder Reranking**. Powered by **LlamaParse** for multimodal, table-aware document ingestion (PDFs, HTML, Text).
    * **Engine 2 (Structured Data):** Autonomous Pandas Agent that executes raw Python code against spreadsheets (Excel/CSV) for 100% mathematical accuracy.
* **📈 LLMOps Observability:** Full integration with **LangSmith** for real-time latency tracking, token cost monitoring, and hallucination auditing.
* **📊 Professional Reporting Engine:** One-click PDF report generation for all financial and data insights using ReportLab.
* **🤖 Autonomous MCP Agent:** A LangGraph React Agent linked to a custom FastMCP server for real-time web tools.

Everything runs locally (compute/database) with secure, enterprise-grade infrastructure.

---

## Workspace Architecture

```text
vignatrix-ragone/
├── backend/ 
│   ├── guardrails_config/     NVIDIA NeMo safety policies
│   ├── rag/ 
│   │   ├── excel_agent.py     Autonomous Pandas/Python execution engine
│   │   ├── vectorstore.py     PostgreSQL + pgvector hybrid-search batching engine
│   │   └── ...                LlamaParse loaders, LangGraph chains
│   ├── pdf_generator.py       ReportLab-based PDF export engine
│   ├── routers/               Modular API endpoints
│   ├── ...                    (auth, database, models, schemas, main.py)
│   └── requirements.txt
├── data/                      Knowledge base (Excel, CSV, PDF, HTML)
├── frontend/                  React (Vite) + Tailwind CSS SPA Client
│   └── src/
│       ├── components/        ChatMessage.jsx (with PDF download button)
│       └── ...
└── docker-compose.yml         Spins up FastAPI, PostgreSQL/pgvector, and Frontend

```

---

## Prerequisites

1. **[Ollama Engine](https://ollama.com)** actively operational.
2. Pull required local assets:

```bash
ollama pull gemma4:12b
ollama pull nomic-embed-text

```

3. **Docker Desktop** installed and running (for PostgreSQL database).
4. **Python 3.11+** and **Node.js 18+**.

---

## Quick Launch (Docker)

Ensure Docker Desktop is operational, configure your `.env` file, and then run:

```bash
docker compose up --build -d

```

Access the interface at: **http://localhost:5174**

---

## The Enterprise Workflow Guide

### 1. The Dual-Engine Intelligence

Your system handles two distinct data types differently using a smart routing mechanism:

* **Documents (PDF/HTML):** Ingested via LlamaCloud's multimodal parser to maintain table fidelity. Stored in **PostgreSQL/pgvector**. The system utilizes hybrid search (Semantic + Keyword) and reranks the results before sending them to the LLM to guarantee zero hallucinations.
* **Spreadsheets (Excel/CSV):** The system bypasses vector search and invokes the `excel_agent.py`. It writes and executes Python code in a safe sandbox to perform grouping, filtering, and complex financial math (e.g., Profit Margins, ROI).

### 2. Audit-Ready Tracing (LangSmith)

Every prompt, retrieval step, and Python execution is logged to your LangSmith dashboard. You can monitor exactly what the AI was "thinking" during execution, track local token speeds, and debug complex LangGraph agent loops.

### 3. Professional Reporting

* Once the system produces a financial result, click the **"Download PDF"** icon in the message bubble.
* The system instantly generates a branded, formatted PDF report containing the analysis insight and source tracking.

---

## Environment Property Management (`backend/.env`)

| Property Key | Default Value | Usage Scope |
| --- | --- | --- |
| `SECRET_KEY` | *Auto-Generated* | JWT security salt |
| `DATABASE_URL` | `postgresql://user:password@db:5432/rag_db` | PostgreSQL connection string |
| `OLLAMA_BASE_URL` | `http://host.docker.internal:11434` | Local LLM Engine Bridge |
| `OLLAMA_LLM_MODEL` | `gemma4:12b` | Reasoning/Code Engine |
| `LLAMA_CLOUD_API_KEY` | `llx-...` | LlamaParse Multimodal ingestion |
| `LANGCHAIN_API_KEY` | `lsv2_...` | LangSmith Observability |
| `LANGCHAIN_TRACING_V2` | `true` | Enables active LLMOps tracing |

```

```