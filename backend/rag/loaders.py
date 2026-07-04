"""
File-type-aware document loading.

Given a path on disk, `load_documents` picks the right LangChain loader
(or a small custom one, for spreadsheets) and returns a list of
`Document` objects ready to be chunked and embedded.
"""
from pathlib import Path

import pandas as pd
from langchain_community.document_loaders import BSHTMLLoader, PyPDFLoader
from langchain_core.documents import Document

SUPPORTED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".html", ".htm"}


class UnsupportedFileTypeError(ValueError):
    """Raised when a file extension isn't one we know how to ingest."""


def _load_excel(path: Path) -> list[Document]:
    """Converts every sheet of a workbook into one Document per sheet.

    Each sheet is rendered as a markdown table so the LLM can reason about
    rows/columns the same way it would about any other block of text.
    """
    sheets = pd.read_excel(path, sheet_name=None)
    documents = []
    for sheet_name, df in sheets.items():
        if df.empty:
            continue
        table_text = df.to_markdown(index=False)
        content = f"Sheet: {sheet_name}\n\n{table_text}"
        documents.append(
            Document(
                page_content=content,
                metadata={"source": path.name, "sheet": sheet_name},
            )
        )
    return documents


def _load_pdf(path: Path) -> list[Document]:
    loader = PyPDFLoader(str(path))
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = path.name
    return docs


def _load_html(path: Path) -> list[Document]:
    loader = BSHTMLLoader(str(path))
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = path.name
    return docs


def load_documents(path: Path) -> list[Document]:
    """Loads a file into a list of LangChain Documents based on its extension."""
    extension = path.suffix.lower()

    if extension == ".pdf":
        return _load_pdf(path)
    if extension in (".xlsx", ".xls"):
        return _load_excel(path)
    if extension in (".html", ".htm"):
        return _load_html(path)

    raise UnsupportedFileTypeError(
        f"Unsupported file type '{extension}'. Supported types: "
        f"{', '.join(sorted(SUPPORTED_EXTENSIONS))}"
    )
