
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

print(SUPABASE_URL)
from supabase import create_client

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

records = [
    {
        "pan_number": "ABCDE1234F",
        "score": 750,
        "total_active_loans": 2,
        "default_history": False,
        "credit_utilization": 35,
        "enquiries_last_6m": 1,
        "age_of_credit_history_months": 48
    },
    {
        "pan_number": "XYZAB9876C",
        "score": 580,
        "total_active_loans": 5,
        "default_history": True,
        "credit_utilization": 92,
        "enquiries_last_6m": 12,
        "age_of_credit_history_months": 24
    },
    {
        "pan_number": "QBPPS3ZOOE",
        "score": 810,
        "total_active_loans": 1,
        "default_history": False,
        "credit_utilization": 18,
        "enquiries_last_6m": 0,
        "age_of_credit_history_months": 96
    },
    {
        "pan_number": "LMNOP4321Q",
        "score": 690,
        "total_active_loans": 3,
        "default_history": False,
        "credit_utilization": 55,
        "enquiries_last_6m": 4,
        "age_of_credit_history_months": 60
    },
    {
        "pan_number": "GHIJK1111L",
        "score": 720,
        "total_active_loans": 4,
        "default_history": False,
        "credit_utilization": 40,
        "enquiries_last_6m": 2,
        "age_of_credit_history_months": 72
    },
    {
        "pan_number": "TUVWX2222M",
        "score": 640,
        "total_active_loans": 6,
        "default_history": True,
        "credit_utilization": 88,
        "enquiries_last_6m": 8,
        "age_of_credit_history_months": 30
    },
    {
        "pan_number": "QRSTU3333N",
        "score": 780,
        "total_active_loans": 2,
        "default_history": False,
        "credit_utilization": 22,
        "enquiries_last_6m": 1,
        "age_of_credit_history_months": 84
    },
    {
        "pan_number": "ABCDE4444P",
        "score": 520,
        "total_active_loans": 7,
        "default_history": True,
        "credit_utilization": 97,
        "enquiries_last_6m": 15,
        "age_of_credit_history_months": 18
    },
    {
        "pan_number": "JKLMN5555R",
        "score": 670,
        "total_active_loans": 3,
        "default_history": False,
        "credit_utilization": 65,
        "enquiries_last_6m": 5,
        "age_of_credit_history_months": 42
    },
    {
        "pan_number": "VWXYZ6666S",
        "score": 845,
        "total_active_loans": 0,
        "default_history": False,
        "credit_utilization": 5,
        "enquiries_last_6m": 0,
        "age_of_credit_history_months": 120
    }
]

supabase.table("credit_bureau_data").insert(records).execute()


