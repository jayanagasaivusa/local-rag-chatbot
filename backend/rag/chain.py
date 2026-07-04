"""
Builds the retrieval-augmented generation chain: retrieve relevant chunks
from Chroma, stuff them into a prompt, and ask the local Ollama model to
answer. Implemented with LangChain Expression Language (LCEL) so each
stage (retrieve -> format -> prompt -> generate) is explicit and testable.
"""
from functools import lru_cache

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_ollama import ChatOllama

from config import OLLAMA_BASE_URL, OLLAMA_LLM_MODEL, RETRIEVER_TOP_K
from rag.vectorstore import get_vectorstore

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using only the "
    "context provided below, which was retrieved from the user's own "
    "documents. If the context does not contain enough information to "
    "answer confidently, say so explicitly instead of guessing. Be "
    "concise and cite specific details from the context when relevant."
)

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ]
)


def _format_docs(docs: list[Document]) -> str:
    if not docs:
        return "(no relevant documents found)"
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


@lru_cache(maxsize=1)
def get_llm() -> ChatOllama:
    return ChatOllama(model=OLLAMA_LLM_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.2)


@lru_cache(maxsize=1)
def build_rag_chain():
    """Returns an LCEL chain: question (str) -> {"answer": str, "docs": [Document]}."""
    retriever = get_vectorstore().as_retriever(search_kwargs={"k": RETRIEVER_TOP_K})
    llm = get_llm()

    generation_step = (
        {
            "context": lambda x: _format_docs(x["docs"]),
            "question": lambda x: x["question"],
        }
        | PROMPT
        | llm
        | StrOutputParser()
    )

    return RunnableParallel(docs=retriever, question=RunnablePassthrough()) | RunnableParallel(
        answer=generation_step,
        docs=lambda x: x["docs"],
    )


def answer_question(question: str) -> dict:
    """Runs the full RAG pipeline and returns the answer plus source filenames."""
    chain = build_rag_chain()
    result = chain.invoke(question)
    sources = sorted(
        {doc.metadata.get("source", "unknown") for doc in result["docs"]}
    )
    return {"response": result["answer"], "sources": sources}
