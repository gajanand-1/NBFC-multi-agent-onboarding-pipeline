"""
tools/communication_tools.py
==============================
Email dispatch used by Agent 3.
Plain function — always called once at the end of the pipeline.
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


NBFC_CONFIG = {
    "signer_name":   "Priya Sharma",
    "signer_title":  "Customer Relations Manager",
    "support_email": "support@yournbfc.com",
    "support_phone": "+91-9876543210",
}


def send_customer_email(
    customer_name:  str,
    customer_email: str,
    subject:        str,
    body:           str
) -> bool:
    """Sends a real transactional email via SendGrid. Returns True on success."""
    api_key    = os.environ.get("SENDGRID_API_KEY1")
    from_email = os.environ.get("SENDGRID_FROM_EMAIL")
    print(f"  Sending to : {customer_email}")
    print(f"  From       : {from_email}")

    if not api_key or not from_email:
        print("  Missing SENDGRID_API_KEY1 or SENDGRID_FROM_EMAIL in .env")
        return False

    message = Mail(
        from_email=from_email,
        to_emails=customer_email,
        subject=subject,
        plain_text_content=body,
    )
    try:
        sg       = SendGridAPIClient(api_key)
        response = sg.send(message)
        success  = response.status_code in (200, 201, 202)
        print(f"  SendGrid response: {response.status_code}")
        return success
    except Exception as e:
        print(f"  Failed to send email: {e}")
        if hasattr(e, "body"):
            print(f"  Error body: {e.body}")
        return False
