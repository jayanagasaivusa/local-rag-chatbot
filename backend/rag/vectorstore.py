"""
Manages the singleton PGVector store instance backed by local Ollama
embeddings. All ingestion and retrieval code should go through
`get_vectorstore()`. Includes custom hybrid search capabilities.
"""
from functools import lru_cache
from langchain_postgres.vectorstores import PGVector
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank

from config import (
    DATABASE_URL,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_MODEL,
)

COLLECTION_NAME = "rag_documents"

@lru_cache(maxsize=1)
def get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(model=OLLAMA_EMBED_MODEL, base_url=OLLAMA_BASE_URL)

@lru_cache(maxsize=1)
def get_vectorstore():
    # Use PGVector instead of Chroma
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )

def build_advanced_hybrid_retriever(base_retriever, top_k=10) -> ContextualCompressionRetriever:
    """
    Hybrid Retriever: Dynamically seeds BM25 from the database store,
    blends it with PGVector via EnsembleRetriever, and applies Flashrank.
    """
    # 1. Fetch current document chunks from Postgres to populate the keyword index
    vectorstore = get_vectorstore()
    
    try:
        # We fetch the raw text chunks out of the underlying vector store
        # using the correct SQLAlchemy session/connection layer inside PGVector
        with vectorstore.Connection(vectorstore.connection_string) as conn:
            with conn.cursor() as cur:
                # Queries the default langchain storage table structure
                cur.execute("SELECT document, cmetadata FROM langchain_pg_embedding;")
                rows = cur.fetchall()
                
        all_docs = [
            Document(page_content=row[0], metadata=row[1] or {}) 
            for row in rows
        ]
    except Exception as e:
        print(f"[HYBRID SEARCH WARNING] Could not dynamically seed BM25: {e}")
        all_docs = []

    # 2. Setup the Sparse Keyword Retriever with real data
    if all_docs:
        bm25_retriever = BM25Retriever.from_documents(all_docs)
        bm25_retriever.k = top_k
    else:
        # Fallback if the database is brand new and completely empty
        bm25_retriever = BM25Retriever.from_documents([Document(page_content="empty table")])
        bm25_retriever.k = 1

    # 3. Create the Hybrid Ensemble mix
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, base_retriever],
        weights=[0.4, 0.6]  # 40% Keyword, 60% Semantic
    )

    # 4. Bind the Local Flashrank Cross-Encoder Reranker
    compressor = FlashrankRerank(top_n=5)
    
    return ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=ensemble_retriever
    )

def split_documents(documents: list[Document]) -> list[Document]:
    """
    Intelligently splits files. Standard files (PDFs, TXT) use recursive chunking.
    Spreadsheets are split row-by-row with header preservation.
    """
    final_chunks = []
    standard_docs = []
    
    for doc in documents:
        source_path = str(doc.metadata.get("source", "")).lower()
        
        if source_path.endswith(('.xlsx', '.xls', '.csv')):
            lines = doc.page_content.split("\n")
            lines = [line.strip() for line in lines if line.strip()]
            if len(lines) < 2:
                standard_docs.append(doc)
                continue
            header_line = lines[0]
            data_lines = lines[1:]
            rows_per_chunk = 4
            for i in range(0, len(data_lines), rows_per_chunk):
                batch_rows = data_lines[i : i + rows_per_chunk]
                chunk_content = f"Table Headers: {header_line}\n" + "\n".join(batch_rows)
                final_chunks.append(
                    Document(page_content=chunk_content, metadata=doc.metadata.copy())
                )
        else:
            standard_docs.append(doc)

    if standard_docs:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        final_chunks.extend(splitter.split_documents(standard_docs))
        
    return final_chunks

def add_documents(documents: list[Document]) -> int:
    """Splits and embeds `documents` into the PGVector store in batches."""
    chunks = split_documents(documents)
    if not chunks:
        return 0

    vectorstore = get_vectorstore()
    
    # THE UPGRADE: Batch processing to protect local Ollama from OOM (Out of Memory) crashes
    batch_size = 25  # Process 25 chunks at a time
    total_batches = (len(chunks) // batch_size) + 1
    
    print(f"\n[VECTOR STORE] Preparing to embed {len(chunks)} chunks in {total_batches} batches...")
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        print(f" -> Processing batch { (i // batch_size) + 1 } of {total_batches}...")
        try:
            vectorstore.add_documents(batch)
        except Exception as e:
            print(f"[ERROR] Ollama choked on batch { (i // batch_size) + 1 }: {e}")
            # If a batch fails, we skip it so the whole 300-page document doesn't crash
            continue
            
    print("[VECTOR STORE] Ingestion complete!")
    return len(chunks)

def list_ingested_sources() -> list[str]:
    """Returns a list of sources. (Placeholder for PGVector source tracking)"""
    # In a real enterprise app, you'd query a tracking table for sources.
    # Returning an empty list or a custom logic here to prevent crashes.
    return []