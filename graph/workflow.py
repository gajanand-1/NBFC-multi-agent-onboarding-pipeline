"""
graph/workflow.py
==================
Assembles all agent nodes into the LangGraph pipeline.
Imports from agents/ only — no business logic lives here.

Graph flow:
  START
    └── extract_docs
          └── verify_identity
                └── verify_address_recency
                      ├── [KYC FAILED]  → END  (fast-path rejection)
                      └── [KYC PASSED]  → calculate_ratios
                                              └── underwrite_loan
                                                    └── communicate_customer
                                                          └── END
"""

from langgraph.graph import StateGraph, START, END

from state.schema import VerificationState

from agents.document_verifier import (
    extract_documents_node,
    verify_identity_node,
    verify_address_and_recency_node,
)
from agents.risk_assessor import (
    calculate_financial_ratios_node,
    credit_underwriting_node,
)
from agents.customer_communicator import customer_communicator_node


# ── Conditional router ───────────────────────────────────────────

def check_kyc_status(state: VerificationState) -> str:
    if (
        not state["pan_verified"]
        or not state["name_match"]
        or not state["address_match"]
        or not state["recency_match"]
    ):
        print("--- CRITICAL KYC FAILURE: ROUTING STRAIGHT TO REJECTION ---")
        return "reject_fast_path"
    return "proceed_to_risk"


# ── Build graph ──────────────────────────────────────────────────

builder = StateGraph(VerificationState)

# Agent 1 nodes
builder.add_node("extract_docs",          extract_documents_node)
builder.add_node("verify_identity",       verify_identity_node)
builder.add_node("verify_address_recency", verify_address_and_recency_node)

# Agent 2 nodes
builder.add_node("calculate_ratios", calculate_financial_ratios_node)
builder.add_node("underwrite_loan",  credit_underwriting_node)

# Agent 3 node
builder.add_node("communicate_customer", customer_communicator_node)

# Edges
builder.add_edge(START,              "extract_docs")
builder.add_edge("extract_docs",     "verify_identity")
builder.add_edge("verify_identity",  "verify_address_recency")

builder.add_conditional_edges(
    "verify_address_recency",
    check_kyc_status,
    {
        "reject_fast_path": END,
        "proceed_to_risk":  "calculate_ratios",
    }
)

builder.add_edge("calculate_ratios",    "underwrite_loan")
builder.add_edge("underwrite_loan",     "communicate_customer")
builder.add_edge("communicate_customer", END)

# Exported pipeline — imported by backend.py and main.py
pipeline = builder.compile()
