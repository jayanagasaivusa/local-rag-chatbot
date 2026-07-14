"""
Manages the singleton Chroma vector store instance backed by local Ollama
embeddings. All ingestion and retrieval code should go through
`get_vectorstore()` so there's only ever one connection to the on-disk
Chroma index.
"""
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

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


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]  # Add this line
    )
    return splitter.split_documents(documents)


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
