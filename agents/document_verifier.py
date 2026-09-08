"""
agents/document_verifier.py
=============================
Agent 1 — Document Verifier

Three nodes wired in sequence inside LangGraph:
  extract_documents_node        → OCR all 3 docs, structured extraction
  verify_identity_node          → name match PAN vs Aadhaar
  verify_address_and_recency_node → LLM address comparison + recency check
"""

import os
from datetime import datetime
from typing import Dict, Any

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from state.schema import VerificationState, ExtractedDocumentData, AddressMatchResult
from tools.document_tools import extract_text


llm = ChatGroq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API"))


# ── Node 1: Extract all documents ───────────────────────────────

def extract_documents_node(state: VerificationState) -> dict:
    print("--- EXTRACTING DOCUMENTS ---")
    paths = state["file_paths"]

    pan_text     = extract_text(paths["pan"])
    aadhaar_text = extract_text(paths["aadhaar"])
    bank_text    = extract_text(paths["bank_statement"])

    combined_text = f"""PAN DOCUMENT:{pan_text}
                    AADHAAR DOCUMENT:{aadhaar_text}

                    BANK STATEMENT:{bank_text}
                    """

    structured_llm = llm.with_structured_output(ExtractedDocumentData)
    result = structured_llm.invoke(
        f"""
        You are a precise KYC Document Extraction System.

        Extract information from the provided PAN Card, Aadhaar Card, and Bank Statement.

        Rules:
        * Extract only information present in the document.
        * Do not guess, infer, or generate missing values.
        * If a field is unreadable or cannot be determined with high confidence, return "ILLEGIBLE".
        * Preserve names, addresses, dates, and identifiers exactly as they appear.
        * You may correct obvious OCR artifacts only when the correction is highly certain.
        * Do not modify names, addresses, identifiers, dates, or financial values based on assumptions.
        * Ignore logos, slogans, watermarks, and decorative text.
        * Return output strictly according to the provided schema.

        Documents:
        {combined_text}
        """
    )

    return {"extracted_data": result.model_dump()}


# ── Node 2: Verify identity — name match ────────────────────────

def verify_identity_node(state: VerificationState) -> Dict[str, Any]:
    print("--- VERIFYING IDENTITY ---")
    data    = state["extracted_data"]
    reasons = []

    name_match = data["pan_name"].lower() == data["aadhaar_name"].lower()
    if not name_match:
        reasons.append("Name mismatch between PAN and Aadhaar.")

    return {
        "pan_verified":     True,
        "aadhaar_verified": True,
        "name_match":       name_match,
        "reasons":          reasons,
    }


# ── Node 3: Verify address (via LLM) + recency ──────────────────

def verify_address_and_recency_node(state: VerificationState) -> dict:
    print("--- VERIFYING ADDRESS (VIA LLM) & RECENCY ---")
    data    = state["extracted_data"]
    reasons = state.get("reasons", [])

    # LLM semantic address comparison
    address_prompt = HumanMessage(content=f"""
    You are a strict but intelligent KYC compliance officer.
    Compare these two addresses to determine if they represent the SAME location.
    Ignore minor OCR typos (like SIO vs S/O), punctuation, and formatting.

    Aadhaar Address: {data['aadhaar_address']}
    Bank Address: {data['bank_address']}
    """)

    address_llm  = llm.with_structured_output(AddressMatchResult)
    match_result = address_llm.invoke([address_prompt])

    if not match_result.is_match:
        reasons.append(f"Address mismatch: {match_result.reason}")

    # Recency check — plain Python
    statement_date = datetime.strptime(data["bank_statement_date"], "%Y-%m-%d")
    days_old       = (datetime.now() - statement_date).days
    recency_match  = days_old <= 90

    if not recency_match:
        reasons.append(f"Bank statement is {days_old} days old. Limit is 90 days.")

    return {
        "address_match": match_result.is_match,
        "recency_match": recency_match,
        "reasons":       reasons,
    }
