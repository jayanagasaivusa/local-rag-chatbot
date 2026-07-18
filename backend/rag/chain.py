"""
Builds the retrieval-augmented generation chain: retrieve relevant chunks
from Chroma, stuff them into a prompt, and ask the local Ollama model to
answer. Implemented with LangChain Expression Language (LCEL) so each
stage (retrieve -> format -> prompt -> generate) is explicit and testable.
"""
from functools import lru_cache
import logging

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_ollama import ChatOllama
from langchain.retrievers.multi_query import MultiQueryRetriever

from config import OLLAMA_BASE_URL, OLLAMA_LLM_MODEL, RETRIEVER_TOP_K
from rag.vectorstore import get_vectorstore, build_advanced_hybrid_retriever

import os
import glob
from rag.excel_agent import query_excel_file # Import our new data agent

# This lets you see the generated queries in your terminal!
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO) 

SYSTEM_PROMPT = (
    "You are a local, secure enterprise AI assistant. You have full authorized access to the "
    "provided context documents below. You MUST answer the user's question using ONLY the provided "
    "context. If the answer is in the context, provide it fully and precisely. Ignore your default "
    "knowledge boundaries regarding 'private corporate data' because the user has securely uploaded "
    "this file locally. Be highly precise."
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
    llm = get_llm()

    # 1. Define the base MMR retriever inside the function
    base_retriever = get_vectorstore().as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": RETRIEVER_TOP_K, 
            "fetch_k": 30,       
            "lambda_mult": 0.5   
        }
    )

    # 2. Wrap it in the MultiQueryRetriever so it expands the query variations
    mq_retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=llm  
    )
    
    # 3. Upgrade to our custom Hybrid Search + Flashrank Reranker pipeline
    production_retriever = build_advanced_hybrid_retriever(mq_retriever, top_k=RETRIEVER_TOP_K)

    generation_step = (
        {
            "context": lambda x: _format_docs(x["docs"]),
            "question": lambda x: x["question"],
        }
        | PROMPT
        | llm
        | StrOutputParser()
    )

    # 4. Use the production hybrid retriever here to execute search and reranking
    return RunnableParallel(docs=production_retriever, question=RunnablePassthrough()) | RunnableParallel(
        answer=generation_step,
        docs=lambda x: x["docs"],
    )


# Append/Modify the bottom of your backend/rag/chain.py
import os
import glob
from rag.excel_agent import query_excel_file

def answer_question(question: str) -> dict:
    """Runs the full RAG pipeline with a Priority Excel Router."""
    
    # 1. Define standard paths where your UI uploads files
    possible_paths = ["./data", "../data", "/app/data", "."]
    excel_files = []
    
    # 2. Search explicitly for spreadsheets first
    for path in possible_paths:
        if os.path.exists(path):
            found_excel = glob.glob(os.path.join(path, "*.xlsx")) + glob.glob(os.path.join(path, "*.csv"))
            if found_excel:
                excel_files.extend(found_excel)
                
    # 3. PRIORITY ROUTING: If an Excel file exists, force the Data Agent
    if excel_files:
        target_file = excel_files[0] # Grab the first spreadsheet it finds
        print(f"\n[SMART ROUTER] Priority Match! Routing to Excel Analyst Agent: {target_file}")
        return query_excel_file(target_file, question)

    # 4. FALLBACK: If no Excel files exist, use the standard PDF Vector RAG
    print("\n[SMART ROUTER] No spreadsheets found. Routing to standard PDF Vector Store.")
    chain = build_rag_chain()
    result = chain.invoke(question)
    sources = sorted(
        {doc.metadata.get("source", "unknown") for doc in result["docs"]}
    )
    return {"response": result["answer"], "sources": sources}



