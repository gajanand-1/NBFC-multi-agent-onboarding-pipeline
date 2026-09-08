"""
main.py
========
Run the pipeline directly from terminal for testing.
Does NOT start the web server — use uvicorn for that.

Usage:
  python main.py
"""

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from graph.workflow import pipeline

if __name__ == "__main__":
    initial_input = {
        "file_paths": {
            "pan":            "documents/PAN.jpeg",
            "aadhaar":        "documents/aadhaar_card.png",
            "bank_statement": "documents/Statement.pdf",
        },
        "monthly_income":        50000.0,
        "existing_emis":         20000.0,
        "requested_loan_amount": 500000,
        "employment_type":       "SALARIED",
        "customer_email":        "gajanandkumarsah@gmail.com",
    }

    final_state = pipeline.invoke(initial_input)

    print("\n========== FINAL RESULT ==========")

    if "risk_decision" not in final_state:
        # KYC fast-path rejection — pipeline ended before risk assessment ran.
        print("Decision    : REJECT (KYC verification failed)")
        print(f"Reasons     : {final_state.get('reasons')}")
    else:
        print(f"Decision    : {final_state['risk_decision']}")
        print(f"Risk Score  : {final_state.get('risk_score')}%")
        print(f"CIBIL Score : {final_state.get('cibil_score')}")
        print(f"DTI Ratio   : {final_state.get('debt_to_income_ratio', 0):.2%}")
        print(f"Email Sent  : {final_state.get('notification_sent')}")
        print(f"Subject     : {final_state.get('email_subject')}")
        print(f"\nReasoning:\n{final_state.get('underwriting_reasoning')}")
