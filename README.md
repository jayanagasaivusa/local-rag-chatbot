# Local RAG Chatbot

A full-stack, fully local Retrieval-Augmented Generation chatbot. Upload PDF, Excel,
or HTML documents; they're chunked, embedded, and stored in ChromaDB; then chat with
a local Ollama model that answers using retrieved context from your documents.

Everything runs on your machine — no data leaves your computer.

## Architecture

```
rag-web app/
├── backend/                 FastAPI + LangChain + Chroma + Ollama
│   ├── main.py               API entrypoint (/upload, /chat, /documents, /health)
│   ├── config.py             Env-driven configuration
│   ├── rag/
│   │   ├── loaders.py         PDF / Excel / HTML -> LangChain Documents
│   │   ├── vectorstore.py     Chroma singleton, chunking, ingestion
│   │   └── chain.py           LCEL retrieval-augmented generation chain
│   ├── data/                  Uploaded source files (gitignored)
│   ├── chroma_db/              Persisted vector index (gitignored)
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 React (Vite) + Tailwind CSS
│   └── src/
│       ├── App.jsx             Layout: sidebar + chat window
│       ├── api.js              Fetch wrapper for the backend API
│       └── components/
│           ├── FileUpload.jsx   Drag-and-drop upload zone
│           ├── Chatbox.jsx      Message list + input + "Thinking..." state
│           └── ChatMessage.jsx  User/AI chat bubble
└── start.sh                  Convenience script to run both servers at once
```

## Prerequisites

### 🚀 Quick Start (Docker)
The easiest way to run this application is using Docker Compose. Make sure Docker Desktop is running on your machine, then run this single command in your terminal:

`docker compose up --build -d`

Once the containers are built and running, open your browser and navigate to: **http://localhost:5174**

1. **[Ollama](https://ollama.com)** installed and running locally.
2. Pull the LLM and embedding models used by default:

   ```bash
   ollama pull gemma4:12b
   ollama pull nomic-embed-text
   ```

   (You can swap either model via the backend `.env` file — see below.)
3. **Python 3.11+** and **Node.js 18+**.

## 1. Backend setup (FastAPI)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env              # adjust model names / ports if needed
```

Run the API server:

```bash
uvicorn main:app --reload --port 8000
```

The API is now live at `http://localhost:8000` (interactive docs at `/docs`).

## 2. Frontend setup (React + Vite)

In a **second terminal**:

```bash
cd frontend
npm install
cp .env.example .env              # adjust VITE_API_BASE_URL if needed
npm run dev
```

The app is now live at `http://localhost:5174`.

## 3. Run both together

Once both `backend/venv` and `frontend/node_modules` exist, you can start everything
with a single command from the project root:

```bash
./start.sh
```

This starts the backend on port `8000` and the frontend on port `5174`, and stops
both cleanly on `Ctrl+C`.

## Using the app

1. Open `http://localhost:5174`.
2. Drag a PDF, Excel (`.xlsx`/`.xls`), or HTML file onto the upload zone in the
   sidebar (or click to browse). Wait for the "✅ Added N chunks" confirmation.
3. Ask a question in the chat box. The backend retrieves the most relevant chunks
   from Chroma and asks your local Ollama model to answer using that context.
   Responses include the source filename(s) used.

## Configuration reference (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `DATA_DIR` | `./data` | Where uploaded files are saved |
| `CHROMA_DIR` | `./chroma_db` | Where the Chroma index is persisted |
| `CHROMA_COLLECTION_NAME` | `rag_documents` | Chroma collection name |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama server URL |
| `OLLAMA_LLM_MODEL` | `gemma4:12b` | Chat/generation model |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `1000` / `150` | Text splitter tuning |
| `RETRIEVER_TOP_K` | `4` | Number of chunks retrieved per question |
| `FRONTEND_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5174` | CORS allow-list |

## Notes

- The vector store persists across restarts (it's just files under `backend/chroma_db`).
  Delete that folder to reset your knowledge base.
- To add support for another file type, add a loader function in
  `backend/rag/loaders.py` and register its extension in `SUPPORTED_EXTENSIONS`.
- This was verified end-to-end locally: uploading a PDF and an Excel file, then
  asking questions answered correctly from each source with correct citations.
