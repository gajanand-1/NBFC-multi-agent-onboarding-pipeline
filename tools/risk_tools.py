"""
tools/risk_tools.py
====================
Credit risk helpers used by Agent 2 (Risk Assessor).

  call_credit_bureau_tool() — fetches CIBIL from Supabase
  policy_retriever          — FAISS RAG retriever over Guidelines/ PDFs

Both are plain functions / objects (not @tool) because Agent 2
calls them in a fixed deterministic sequence — no LLM loop needed.
"""

import os
from supabase import create_client
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# ── Supabase client ──────────────────────────────────────────────

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)


# ── CIBIL fetch (from your cell 11) ─────────────────────────────

def call_credit_bureau_tool(pan_number: str):
    print(f"--- FETCHING CREDIT BUREAU DATA FOR PAN: {pan_number[:5]}***** ---")
    response = (
        supabase.table("credit_bureau_data")
        .select("*")
        .eq("pan_number", pan_number)
        .execute()
    )
    if response.data:
        return response.data[0]
    return None


# ── RAG policy retriever (from your cells 13,14) ────────────────

def setup_policy_retriever():
    """Loads all PDFs from Guidelines/ into FAISS. Called once at startup."""
    loader   = PyPDFDirectoryLoader("Guidelines")
    docs     = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    splits   = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.from_documents(splits, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 10})


# Initialised once when this module is first imported
policy_retriever = setup_policy_retriever()
