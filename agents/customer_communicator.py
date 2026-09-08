"""
agents/customer_communicator.py
=================================
Agent 3 — Customer Communicator

One node:
  customer_communicator_node → LLM drafts email + SendGrid sends it
"""

import os
from langchain_groq import ChatGroq

from state.schema import VerificationState, EmailDraftSchema
from tools.communication_tools import send_customer_email, NBFC_CONFIG


llm = ChatGroq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API"))


def customer_communicator_node(state: VerificationState) -> dict:
    print("--- DRAFTING & SENDING CUSTOMER COMMUNICATION ---")

    decision       = state.get("risk_decision", "MANUAL_REVIEW")
    customer_name  = state["extracted_data"].get("pan_name", "Valued Customer").title()
    customer_email = state["customer_email"]
    amount         = state.get("requested_loan_amount", 0)
    reasons        = state.get("reasons", [])

    if decision == "APPROVE":
        interest_rate = "10.5%"
        flagged_issue_note = (
            f"Note: The system flagged this issue: {'; '.join(reasons)}. "
            if reasons else ""
        )
        instructions  = (
            f"Draft a warm, professional onboarding email for an APPROVED loan of INR {amount}. "
            f"Mention the interest rate is {interest_rate}. "
            f"{flagged_issue_note}Mention naturally that an updated "
            f"bank statement is needed before final disbursal. "
            f"Sign off as {NBFC_CONFIG['signer_name']}, {NBFC_CONFIG['signer_title']}. "
            f"Include this contact info naturally: {NBFC_CONFIG['support_email']}, "
            f"{NBFC_CONFIG['support_phone']}. "
            f"Do not invent any other name, phone number, or email."
        )
    elif decision == "REJECT":
        instructions = (
            f"Draft a highly polite, empathetic, and professional decline email for a loan "
            f"request of INR {amount}. Do not sound robotic. Mention that we cannot proceed "
            f"at this time due to our internal risk policies. "
            f"Sign off as {NBFC_CONFIG['signer_name']}, {NBFC_CONFIG['signer_title']}."
        )
    else:  # MANUAL_REVIEW
        instructions = (
            f"Draft a polite email stating the loan application for INR {amount} is under "
            f"manual review by our credit team. Tell them we will get back within 48 hours. "
            f"Sign off as {NBFC_CONFIG['signer_name']}, {NBFC_CONFIG['signer_title']}."
        )

    prompt = [
        ("system", """You are the Customer Communications AI for a premium NBFC.
Write professional, warm, and clear emails like a real relationship manager, not a template.

Strict rules:
- Do NOT use markdown bold (**text**) — write plain prose only.
- Do NOT use numbered lists or bullet points — use natural flowing sentences.
- Do NOT use placeholder brackets like [Your Name] — use the exact details given.
- Keep it to 3-4 short paragraphs maximum.
- Sound like a person who actually read this specific application."""),
        ("human", f"Customer Name: {customer_name}\nInstructions: {instructions}")
    ]

    structured_llm = llm.with_structured_output(EmailDraftSchema)
    email_draft: EmailDraftSchema = structured_llm.invoke(prompt)

    dispatch_success = send_customer_email(
        customer_name=customer_name,
        customer_email=customer_email,
        subject=email_draft.subject,
        body=email_draft.body,
    )

    return {
        "email_subject":     email_draft.subject,
        "email_body":        email_draft.body,
        "notification_sent": dispatch_success,
    }
