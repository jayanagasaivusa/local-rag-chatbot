# Local RAG & Data Intelligence Platform

A secure, full-stack, local AI enterprise architecture featuring user authentication, protected chat histories, NVIDIA safety guardrails, and a **Dual-Engine AI** (Vector-based document intelligence + Autonomous Pandas Data Analyst).

## Core Features

* **🔐 User Authentication:** Secure signup/login via JWT tokens with session-isolated chat history.
* **🛡️ NVIDIA NeMo Guardrails:** Advanced topical, safety, and security guardrail configurations.
* **🧠 Dual-Engine AI Architecture:**
* **Engine 1 (Unstructured):** Vector RAG pipeline using ChromaDB for PDFs, HTML, and Text.
* **Engine 2 (Structured):** Autonomous Pandas Agent that executes raw Python code against spreadsheets (Excel/CSV) for 100% mathematical accuracy.


* **📊 Professional Reporting Engine:** One-click PDF report generation for all financial and data insights.
* **🤖 Autonomous MCP Agent:** A LangGraph React Agent linked to a custom FastMCP server for real-time web tools.

Everything runs locally — zero external API dependency, absolute data privacy.

---

## Workspace Architecture

```text
vignatrix-ragone/
├── backend/ 
│   ├── guardrails_config/     NVIDIA NeMo safety policies
│   ├── rag/ 
│   │   ├── excel_agent.py     Autonomous Pandas/Python execution engine
│   │   └── ...                Loaders, vector store, generation chain
│   ├── pdf_generator.py       ReportLab-based PDF export engine
│   ├── routers/               Modular API endpoints
│   ├── ...                    (auth, database, models, schemas, main.py)
│   └── requirements.txt
├── data/                      Knowledge base (Excel, PDF, HTML, Vector Store)
├── frontend/                  React (Vite) + Tailwind CSS SPA Client
│   └── src/
│       ├── components/        ChatMessage.jsx (with PDF download button)
│       └── ...
└── ...

```

---

## Prerequisites

1. **[Ollama Engine](https://ollama.com)** actively operational.
2. Pull required assets:
```bash
ollama pull gemma4:12b
ollama pull nomic-embed-text

```


3. **Python 3.11+** and **Node.js 18+**.

---

## Quick Launch (Docker)

Ensure Docker Desktop is operational, then:

```bash
docker compose up --build -d

```

Access the interface at: **http://localhost:5174**

---

## The Enterprise Workflow Guide

### 1. The Dual-Engine Intelligence

Your system handles two distinct data types differently:

* **Documents (PDF/HTML):** Ingested into ChromaDB. The system performs semantic similarity search to provide cited answers.
* **Spreadsheets (Excel/CSV):** The system invokes the `excel_agent.py`. It writes and executes Python code in a safe sandbox to perform grouping, filtering, and complex financial math (e.g., Profit Margins, ROM).

### 2. Professional Reporting

* Once the system produces a financial result, click the **"Download PDF"** icon in the message bubble.
* The system uses `reportlab` to instantly generate a branded, formatted PDF report containing the analysis insight and source tracking.

### 3. Adding New Features

* **To tweak analysis logic:** Edit `backend/rag/excel_agent.py`.
* **To change report branding:** Edit `backend/pdf_generator.py`.

---

## Environment Property Management (`backend/.env`)

| Property Key | Default Value | Usage Scope |
| --- | --- | --- |
| `SECRET_KEY` | *Auto-Generated* | JWT security salt |
| `DATABASE_URL` | `sqlite:///./local_rag.db` | User & Session history |
| `OLLAMA_BASE_URL` | `[http://host.docker.internal:11434](http://host.docker.internal:11434)` | LLM Engine Bridge |
| `OLLAMA_LLM_MODEL` | `gemma4:12b` | Reasoning/Code Engine |

---

