import os
from pathlib import Path
from langchain_core.documents import Document
from llama_parse import LlamaParse

SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".docx", ".pptx", ".html"] # LlamaParse supports broad file types

class UnsupportedFileTypeError(Exception):
    pass

def load_documents(file_path: Path | str) -> list[Document]:
    """
    Advanced Data Ingestion: Uses LlamaParse to accurately extract text,
    tables, and complex layouts into clean Markdown format.
    """
    file_path = str(file_path)
    extension = Path(file_path).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(f"File type {extension} is not supported.")

    # Fetch the API key from your .env
    llama_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not llama_key:
        raise ValueError("LLAMA_CLOUD_API_KEY is missing from environment variables.")

    print(f"[DATA INGESTION] Firing up LlamaParse for {Path(file_path).name}...")

    # Initialize the GenAI-native parser
    parser = LlamaParse(
        api_key=llama_key,
        result_type="markdown", # Converts tables perfectly into Markdown syntax
        verbose=True,
        # Premium features: auto_mode enables extraction of charts/visuals
        auto_mode=True,
        auto_mode_trigger_on_table_in_page=True
    )

    # Load and parse the document (Returns LlamaIndex Documents)
    try:
        llama_docs = parser.load_data(file_path)
    except Exception as e:
        print(f"[ERROR] LlamaParse failed: {e}")
        return []

    # Translate LlamaIndex docs to LangChain docs so our VectorStore accepts them seamlessly
    langchain_docs = []
    for doc in llama_docs:
        # We attach the source filename to the metadata for accurate citation reporting
        metadata = doc.metadata or {}
        metadata["source"] = Path(file_path).name 
        
        langchain_docs.append(
            Document(page_content=doc.text, metadata=metadata)
        )

    print(f"[DATA INGESTION] Success! Parsed {len(langchain_docs)} high-fidelity markdown pages.")
    return langchain_docs