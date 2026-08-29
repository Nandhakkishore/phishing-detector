import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def insert_scan(url: str, classification: str, confidence: float, page_fetched: bool):
    result = supabase.table("scans").insert({
        "url": url,
        "classification": classification,
        "confidence": confidence,
        "page_fetched": page_fetched,
    }).execute()
    return result.data


def insert_report(url: str, original_classification: str, user_comment: str | None):
    result = supabase.table("reports").insert({
        "url": url,
        "original_classification": original_classification,
        "user_comment": user_comment,
    }).execute()
    return result.data


def get_statistics():
    scans = supabase.table("scans").select("classification, confidence").execute().data
    reports = supabase.table("reports").select("id").execute().data

    total_scans = len(scans)
    phishing_count = sum(1 for s in scans if s["classification"] == "phishing")
    legitimate_count = sum(1 for s in scans if s["classification"] == "legitimate")
    suspicious_count = sum(1 for s in scans if s["classification"] == "suspicious")
    avg_confidence = (
        sum(s["confidence"] for s in scans) / total_scans if total_scans > 0 else 0.0
    )

    return {
        "total_scans": total_scans,
        "phishing_count": phishing_count,
        "legitimate_count": legitimate_count,
        "suspicious_count": suspicious_count,
        "total_reports": len(reports),
        "average_confidence": round(avg_confidence, 4),
    }


def get_reports(limit: int = 50):
    result = (
        supabase.table("reports")
        .select("*")
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data
