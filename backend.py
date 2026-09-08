"""
backend.py
===========
FastAPI server.
  GET  /          → serves nbfc_ui.html
  POST /run       → accepts uploaded docs + form fields, runs pipeline, returns result
"""

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

import os, shutil
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from graph.workflow import pipeline

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def serve_ui():
    return FileResponse("nbfc_ui.html")


@app.post("/run")
async def run_onboarding(
    pan:                   UploadFile,
    aadhaar:               UploadFile,
    bank_statement:        UploadFile,
    customer_email:        str   = Form(...),
    monthly_income:        float = Form(...),
    existing_emis:         float = Form(...),
    requested_loan_amount: float = Form(...),
    employment_type:       str   = Form(...)
):
    # Save uploaded files to documents/
    os.makedirs("documents", exist_ok=True)

    pan_path  = f"documents/PAN{Path(pan.filename).suffix}"
    adh_path  = f"documents/aadhaar{Path(aadhaar.filename).suffix}"
    bank_path = f"documents/statement{Path(bank_statement.filename).suffix}"

    for upload, path in [
        (pan,           pan_path),
        (aadhaar,       adh_path),
        (bank_statement, bank_path)
    ]:
        with open(path, "wb") as f:
            shutil.copyfileobj(upload.file, f)

    # Run the full pipeline
    result = pipeline.invoke({
        "file_paths": {
            "pan":            pan_path,
            "aadhaar":        adh_path,
            "bank_statement": bank_path,
        },
        "customer_email":        customer_email,
        "monthly_income":        monthly_income,
        "existing_emis":         existing_emis,
        "requested_loan_amount": requested_loan_amount,
        "employment_type":       employment_type,
    })

    # "risk_decision" is only absent when the pipeline fast-path-rejected at
    # KYC (verify_address_recency's conditional edge routes straight to END,
    # so Agent 2/3 never ran) — that must surface as REJECT, not the
    # misleading MANUAL_REVIEW default.
    kyc_failed = "risk_decision" not in result

    # Return full result so the UI can show decision + reasoning + email
    return {
        "decision":             "REJECT" if kyc_failed else result.get("risk_decision", "MANUAL_REVIEW"),
        "kyc_failed":           kyc_failed,
        "email_sent":           result.get("notification_sent",      False),
        "risk_score":           result.get("risk_score",             0),
        "cibil_score":          result.get("cibil_score",            0),
        "dti_ratio":            result.get("debt_to_income_ratio",   0),
        "reasoning":            result.get("underwriting_reasoning", ""),
        "email_subject":        result.get("email_subject",          ""),
        "email_body":           result.get("email_body",             ""),
        "reasons":              result.get("reasons",                []),
    }
