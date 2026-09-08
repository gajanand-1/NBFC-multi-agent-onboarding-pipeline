"""
state/schema.py
================
Single source of truth for:
  - VerificationState  : shared state dict flowing through the entire LangGraph pipeline
  - ExtractedDocumentData : structured output schema for Agent 1 document extraction
  - AddressMatchResult    : structured output schema for address comparison
  - CreditDecisionSchema  : structured output schema for Agent 2 underwriting
  - EmailDraftSchema      : structured output schema for Agent 3 email drafting
"""

from typing import Dict, Any, List, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


# ── Shared pipeline state ────────────────────────────────────────

class VerificationState(TypedDict):

    # ── Inputs (filled before pipeline starts) ──
    file_paths:             Dict[str, str]
    monthly_income:         float
    existing_emis:          float
    requested_loan_amount:  float
    employment_type:        Literal["SALARIED", "SELF_EMPLOYED", "UNEMPLOYED"]
    customer_email:         str

    # ── Agent 1 outputs ──
    extracted_data:   Dict[str, Any]
    pan_verified:     bool
    aadhaar_verified: bool
    name_match:       bool
    address_match:    bool
    recency_match:    bool
    reasons:          List[str]

    # ── Agent 2 outputs ──
    cibil_score:            int
    debt_to_income_ratio:   float
    risk_decision:          Literal["APPROVE", "REJECT", "MANUAL_REVIEW"]
    risk_score:             float
    underwriting_reasoning: str

    # ── Agent 3 outputs ──
    email_subject:    str
    email_body:       str
    notification_sent: bool


# ── Agent 1 schemas ──────────────────────────────────────────────

class ExtractedDocumentData(BaseModel):
    pan_name:           str = Field(description="The full name extracted from the PAN card.")
    pan_number:         str = Field(description="The 10-character alphanumeric PAN number.")
    pan_dob:            str = Field(description="The date of birth from the PAN card.")
    aadhaar_name:       str = Field(description="The full name extracted from the Aadhaar card.")
    aadhaar_address:    str = Field(description="The full address extracted from the Aadhaar card.")
    aadhaar_dob:        str = Field(description="The date of birth from the Aadhaar card.")
    bank_name:          str = Field(description="The account holder's name on the bank statement.")
    bank_address:       str = Field(description="The account holder's address on the bank statement.")
    bank_statement_date: str = Field(description="Most recent statement date in YYYY-MM-DD format.")


class AddressMatchResult(BaseModel):
    is_match: bool = Field(description="True if both addresses represent the same physical location.")
    reason:   str  = Field(description="Brief explanation of why they match or don't match.")


# ── Agent 2 schema ───────────────────────────────────────────────

class CreditDecisionSchema(BaseModel):
    decision: Literal["APPROVE", "REJECT", "MANUAL_REVIEW"] = Field(
        description="Final underwriting decision based on risk profile analysis."
    )
    risk_score_percentage: float = Field(
        description="Internal risk probability from 0% (lowest) to 100% (highest)."
    )
    key_risk_factors: list[str] = Field(
        description="Primary positive or negative factors influencing the decision."
    )
    justification: str = Field(
        description="Detailed professional narrative explaining the reasoning chain."
    )


# ── Agent 3 schema ───────────────────────────────────────────────

class EmailDraftSchema(BaseModel):
    subject: str = Field(description="A professional and engaging email subject line.")
    body:    str = Field(description="The complete email body written to the customer.")
