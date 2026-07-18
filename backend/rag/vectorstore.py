"""
Manages the singleton Chroma vector store instance backed by local Ollama
embeddings. All ingestion and retrieval code should go through
`get_vectorstore()` so there's only ever one connection to the on-disk
Chroma index. Includes custom hybrid search capabilities.
"""
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank

from config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_MODEL,
)


@lru_cache(maxsize=1)
def get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(model=OLLAMA_EMBED_MODEL, base_url=OLLAMA_BASE_URL)


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    return Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(CHROMA_DIR),
    )


def build_advanced_hybrid_retriever(base_retriever, top_k=10) -> ContextualCompressionRetriever:
    """
    Extracts embedded texts from the local Chroma instance, constructs a temporary
    BM25 sparse retriever, blends them via EnsembleRetriever, and applies Flashrank
    reranking for ultra-high keyword accuracy.
    """
    vectorstore = get_vectorstore()
    
    # 1. Safely extract all raw documents currently residing inside ChromaDB
    collection_data = vectorstore.get(include=["documents", "metadatas"])
    
    raw_texts = collection_data.get("documents", [])
    metadatas = collection_data.get("metadatas", [])
    
    chroma_docs = []
    if raw_texts:
        for text, meta in zip(raw_texts, metadatas):
            chroma_docs.append(Document(page_content=text, metadata=meta or {}))

    # 2. Setup the Sparse Keyword Retriever
    # Fallback to base_retriever parameters if database contains no elements yet
    if chroma_docs:
        bm25_retriever = BM25Retriever.from_documents(chroma_docs)
        bm25_retriever.k = top_k
    else:
        bm25_retriever = base_retriever

    # 3. Create the Hybrid Ensemble mix
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, base_retriever],
        weights=[0.4, 0.6]  # 40% exact keyword mapping emphasis, 60% semantic mapping emphasis
    )

    # 4. Bind the Local Flashrank Cross-Encoder Reranker (Selects the best 5 out of everything)
    compressor = FlashrankRerank(top_n=5)
    
    return ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=ensemble_retriever
    )


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Intelligently splits files. Standard files (PDFs, TXT) use recursive chunking.
    Spreadsheets (.xlsx, .xls, .csv) are split row-by-row, keeping the header row 
    attached to every single chunk so the LLM never loses context.
    """
    final_chunks = []
    standard_docs = []
    
    for doc in documents:
        source_path = str(doc.metadata.get("source", "")).lower()
        
        # Check if the document comes from an Excel spreadsheet or CSV file
        if source_path.endswith(('.xlsx', '.xls', '.csv')):
            lines = doc.page_content.split("\n")
            # Clean out any empty rows
            lines = [line.strip() for line in lines if line.strip()]
            
            if len(lines) < 2:
                # If it's too short, just pass it to the standard pool
                standard_docs.append(doc)
                continue
                
            # Treat the first row as the global table header
            header_line = lines[0]
            data_lines = lines[1:]
            
            # Group data rows into blocks of 3 to 5 rows per chunk
            rows_per_chunk = 4
            for i in range(0, len(data_lines), rows_per_chunk):
                batch_rows = data_lines[i : i + rows_per_chunk]
                
                # Reconstruct a mini table structure containing the headers + specific rows
                chunk_content = f"Table Headers: {header_line}\n" + "\n".join(batch_rows)
                
                final_chunks.append(
                    Document(
                        page_content=chunk_content,
                        metadata=doc.metadata.copy()
                    )
                )
        else:
            # It's a standard PDF or text document
            standard_docs.append(doc)

    # Process all standard text/PDF files using your original text splitter config
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
    """Splits and embeds `documents` into the vector store. Returns chunk count."""
    chunks = split_documents(documents)
    if not chunks:
        return 0

    vectorstore = get_vectorstore()
    batch_size = 32
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        vectorstore.add_documents(batch)
    return len(chunks)


def list_ingested_sources() -> list[str]:
    """Returns the distinct set of source filenames currently in the store."""
    vectorstore = get_vectorstore()
    collection = vectorstore.get(include=["metadatas"])
    sources = {
        meta.get("source")
        for meta in collection.get("metadatas", [])
        if meta and meta.get("source")
    }
    return sorted(sources)