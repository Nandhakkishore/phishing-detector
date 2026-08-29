import sys
import os
import secrets
import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "feature_extraction"))
sys.path.append(os.path.join(os.path.dirname(__file__), "services"))
sys.path.append(os.path.dirname(__file__))

from url_features import extract_url_features
from live_content_extractor import extract_live_content_features
from db.database import insert_scan, insert_report, get_statistics, get_reports

app = FastAPI(title="Hybrid Phishing Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "saved_models", "xgboost_hybrid.pkl")
model = joblib.load(MODEL_PATH)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
VALID_TOKENS = set()


FEATURE_COLUMNS = [
    "url_length", "hostname_length", "path_length", "num_dots", "num_hyphens",
    "num_digits", "num_special_chars", "num_underscores", "num_slashes",
    "num_question_marks", "num_equals", "num_at_symbols", "has_ip", "has_https",
    "num_subdomains", "has_port", "is_shortened", "suspicious_word_count",
    "num_redirect_indicators", "hostname_entropy", "digit_ratio", "special_char_ratio",
    "LineOfCode", "LargestLineLength", "HasTitle", "DomainTitleMatchScore",
    "URLTitleMatchScore", "HasFavicon", "Robots", "IsResponsive", "NoOfURLRedirect",
    "NoOfSelfRedirect", "HasDescription", "NoOfPopup", "NoOfiFrame",
    "HasExternalFormSubmit", "HasSocialNet", "HasSubmitButton", "HasHiddenFields",
    "HasPasswordField", "Bank", "Pay", "Crypto", "HasCopyrightInfo", "NoOfImage",
    "NoOfCSS", "NoOfJS", "NoOfSelfRef", "NoOfEmptyRef", "NoOfExternalRef",
]

def normalize_url(url: str) -> str:
    url = url.strip()
    if url.endswith("/") and url.count("/") > 2:
        url = url.rstrip("/")
    return url


class PredictRequest(BaseModel):
    url: str


class ReportRequest(BaseModel):
    url: str
    original_classification: str
    user_comment: str | None = None


class AdminLoginRequest(BaseModel):
    password: str


@app.post("/predict")
def predict(request: PredictRequest):
    url = normalize_url(request.url)

    url_feats = extract_url_features(url)
    content_feats = extract_live_content_features(url)

    fetch_success = content_feats.pop("fetch_success", 0)
    content_feats.pop("fetch_error", None)

    combined = {**url_feats, **content_feats}
    row = {col: combined.get(col, 0) for col in FEATURE_COLUMNS}
    X = pd.DataFrame([row])

    proba = model.predict_proba(X)[0]
    pred_class = int(model.predict(X)[0])
    confidence = float(proba[pred_class])

    if pred_class == 1:
        label = "phishing" if confidence > 0.75 else "suspicious"
    else:
        label = "legitimate" if confidence > 0.75 else "suspicious"

    reasons = _build_reasons(url_feats, content_feats, fetch_success)

    insert_scan(url, label, confidence, bool(fetch_success))

    return {
        "classification": label,
        "confidence": round(confidence, 4),
        "reasons": reasons,
        "page_fetched": bool(fetch_success),
    }


@app.post("/report")
def report(request: ReportRequest):
    data = insert_report(request.url, request.original_classification, request.user_comment)
    report_id = data[0]["id"] if data else None
    return {"status": "report received", "report_id": report_id}


@app.get("/statistics")
def statistics():
    return get_statistics()


@app.get("/reports")
def reports():
    return get_reports()


@app.post("/admin/login")
def admin_login(request: AdminLoginRequest):
    if not ADMIN_PASSWORD or request.password != ADMIN_PASSWORD:
        return {"success": False, "message": "Incorrect password"}
    token = secrets.token_hex(24)
    VALID_TOKENS.add(token)
    return {"success": True, "token": token}


@app.get("/admin/verify")
def admin_verify(token: str):
    return {"valid": token in VALID_TOKENS}


def _build_reasons(url_feats: dict, content_feats: dict, fetch_success: int) -> list:
    reasons = []

    if url_feats.get("has_ip"):
        reasons.append("URL uses an IP address instead of a domain name")
    if not url_feats.get("has_https"):
        reasons.append("Site does not use HTTPS")
    if url_feats.get("suspicious_word_count", 0) > 0:
        reasons.append("URL contains suspicious keywords (e.g. login, verify, secure)")
    if url_feats.get("is_shortened"):
        reasons.append("URL uses a link-shortening service")
    if url_feats.get("url_length", 0) > 100:
        reasons.append("Unusually long URL")

    if not fetch_success:
        reasons.append("Page could not be reached — treated cautiously")
    else:
        if content_feats.get("HasPasswordField"):
            reasons.append("Password input field detected on page")
        if content_feats.get("HasHiddenFields"):
            reasons.append("Hidden form fields detected")
        if content_feats.get("NoOfExternalRef", 0) < 3:
            reasons.append("Very few external references — page may be a stripped-down clone")

    if not reasons:
        reasons.append("No major risk indicators detected")

    return reasons


@app.get("/")
def root():
    return {"status": "Phishing Detection API is running"}
