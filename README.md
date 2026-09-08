# NBFC Onboarding — Multi-Agent Loan Underwriting Pipeline

## Problem Statement

Onboarding a loan applicant at an NBFC traditionally requires a human to
manually cross-check KYC documents (PAN, Aadhaar, bank statement) for
identity and address consistency, pull the applicant's credit bureau score,
calculate their debt-to-income ratio, apply internal lending policy to reach
an approve/reject/review decision, and then communicate that decision back
to the customer. Done manually, this process is slow, inconsistent across
reviewers, and doesn't scale.

## Solution

This project automates the full onboarding flow using a three-agent
pipeline built on LangGraph, where each agent handles one stage of
underwriting and hands verified state to the next.

## Pipeline / Architecture

**Agent 1 — Document Verifier**
Extracts text from the PAN card, Aadhaar card, and bank statement (OCR via
EasyOCR for images, `pypdf` for PDFs), then uses an LLM with a structured
output schema to pull out names, addresses, and dates. It checks that the
name on the PAN matches the Aadhaar, that the Aadhaar and bank statement
addresses refer to the same location (via LLM semantic comparison, tolerant
of OCR noise), and that the bank statement is recent (within 90 days). Any
failure here routes straight to a fast-path rejection — the application
never reaches risk assessment.

**Agent 2 — Risk Assessor**
Runs only if KYC passes. Computes the debt-to-income ratio from declared
income and existing EMIs, fetches the applicant's CIBIL score from a
Supabase-backed credit bureau table, and retrieves the relevant sections of
the NBFC's internal lending policy documents from a FAISS vector store
(RAG) to ground its decision. An LLM then issues a final decision — APPROVE,
REJECT, or MANUAL_REVIEW — along with a risk score and a policy-grounded
justification.

**Agent 3 — Customer Communicator**
Drafts a personalized email appropriate to the outcome (approval,
rejection, or manual review) and sends it to the applicant via SendGrid.

## Application

A FastAPI backend exposes a single `/run` endpoint that accepts the
applicant's details and uploaded documents, runs them through the pipeline,
and returns the decision, risk metrics, and reasoning. A browser-based UI
lets an operator fill in applicant details, upload the three KYC documents,
and watch the agent pipeline execute with live status per stage, finishing
in a clear approve/reject/manual-review result card.

## Tech Stack

- **Orchestration**: LangGraph, LangChain
- **LLM**: Groq (`openai/gpt-oss-120b`)
- **Document extraction**: EasyOCR, pypdf
- **Credit bureau data**: Supabase
- **Policy retrieval (RAG)**: FAISS + HuggingFace sentence-transformer embeddings
- **Email delivery**: SendGrid
- **Backend**: FastAPI
- **Frontend**: static HTML/JS
