"""
agents/risk_assessor.py
=========================
Agent 2 — Risk Assessor

Two nodes wired in sequence inside LangGraph:
  calculate_financial_ratios_node → DTI + CIBIL from Supabase
  credit_underwriting_node        → RAG policy retrieval + LLM decision
"""

import os
from langchain_groq import ChatGroq

from state.schema import VerificationState, CreditDecisionSchema
from tools.risk_tools import call_credit_bureau_tool, policy_retriever


llm = ChatGroq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API"))


# ── Node 1: Financial ratios ─────────────────────────────────────

def calculate_financial_ratios_node(state: VerificationState) -> dict:
    print("--- COMPUTING FINANCIAL RATIOS ---")

    income  = state["monthly_income"]
    emis    = state["existing_emis"]
    pan_num = state["extracted_data"].get("pan_number", "")

    dti_ratio   = (emis / income) if income > 0 else 1.0
    bureau_data = call_credit_bureau_tool(pan_num)

    return {
        "debt_to_income_ratio": dti_ratio,
        "cibil_score":          bureau_data["score"] if bureau_data else 0,
    }


# ── Node 2: RAG underwriting decision ───────────────────────────

def credit_underwriting_node(state: VerificationState) -> dict:
    print("--- GENERATING UNDERWRITING DECISION VIA RAG ---")

    # 1. Compile applicant profile
    applicant_context = f"""
    Applicant Financial Profile:
    - Monthly Income: INR {state.get('monthly_income', 0)}
    - Existing Monthly EMIs: INR {state.get('existing_emis', 0)}
    - Debt-to-Income (DTI) Ratio: {state.get('debt_to_income_ratio', 0):.2%}
    - Credit Bureau (CIBIL) Score: {state.get('cibil_score', 0)}
    - Employment Type: {state.get('employment_type', 'UNKNOWN')}
    - Requested Loan Amount: INR {state.get('requested_loan_amount', 0)}

    Document Verification Summary:
    - Identity & KYC Match: {state.get('name_match', False) and state.get('pan_verified', False)}
    """

    # 2. RAG: retrieve matching policy sections
    search_query = (
        f"Credit underwriting approval rules and thresholds for "
        f"{state.get('employment_type')} applicant with monthly income "
        f"INR {state.get('monthly_income', 0)}, "
        f"DTI {state.get('debt_to_income_ratio', 0):.2%} "
        f"and loan ask {state.get('requested_loan_amount', 0)}."
    )
    retrieved_docs = policy_retriever.invoke(search_query)
    policy_context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    print(f"--- RETRIEVED POLICIES ---\n{policy_context}\n--------------------------")

    # 3. LLM decision grounded in retrieved policy
    prompt = [
        ("system", f"""You are an elite Credit Underwriting AI for a major NBFC.
Analyze the applicant's profile strictly using the Official Policy Guidelines provided below.

<OFFICIAL_POLICY_GUIDELINES>
{policy_context}
</OFFICIAL_POLICY_GUIDELINES>

Rules:
1. Base your decision (APPROVE, REJECT, MANUAL_REVIEW) ONLY on the guidelines above.
2. If the policy text does not cover a specific metric, default to MANUAL_REVIEW.
3. Explain your justification clearly referencing the policy rules."""),
        ("human", applicant_context)
    ]

    structured_underwriter = llm.with_structured_output(CreditDecisionSchema)
    assessment: CreditDecisionSchema = structured_underwriter.invoke(prompt)

    return {
        "risk_decision":          assessment.decision,
        "risk_score":             assessment.risk_score_percentage,
        "underwriting_reasoning": assessment.justification,
    }
