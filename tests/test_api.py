import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()


def test_predict_returns_200():
    response = client.post("/predict", json={"url": "https://www.python.org"})
    assert response.status_code == 200


def test_predict_response_shape():
    response = client.post("/predict", json={"url": "https://www.python.org"})
    data = response.json()
    assert "classification" in data
    assert "confidence" in data
    assert "reasons" in data
    assert "page_fetched" in data
    assert data["classification"] in ["legitimate", "suspicious", "phishing"]
    assert isinstance(data["reasons"], list)
    assert 0.0 <= data["confidence"] <= 1.0


def test_predict_missing_url_field():
    response = client.post("/predict", json={})
    assert response.status_code == 422


def test_predict_handles_unreachable_url():
    response = client.post("/predict", json={"url": "http://192.168.1.1/login-verify-secure"})
    assert response.status_code == 200
    data = response.json()
    assert data["page_fetched"] is False


def test_predict_handles_empty_string_url():
    response = client.post("/predict", json={"url": ""})
    assert response.status_code == 200


def test_trailing_slash_normalization_regression():
    # Regression test for the Day 9 bug: same site with/without trailing slash
    # must produce the same classification after normalization was added.
    r1 = client.post("/predict", json={"url": "https://github.com"})
    r2 = client.post("/predict", json={"url": "https://github.com/"})
    assert r1.json()["classification"] == r2.json()["classification"]


def test_report_requires_classification_field():
    response = client.post("/report", json={"url": "https://example.com"})
    assert response.status_code == 422


def test_report_success():
    response = client.post("/report", json={
        "url": "https://example.com",
        "original_classification": "legitimate",
        "user_comment": "pytest test report",
    })
    assert response.status_code == 200
    assert "report_id" in response.json()


def test_statistics_returns_200():
    response = client.get("/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "total_scans" in data
    assert "phishing_count" in data
    assert "legitimate_count" in data


def test_statistics_counts_are_non_negative():
    response = client.get("/statistics")
    data = response.json()
    assert data["total_scans"] >= 0
    assert data["phishing_count"] >= 0
    assert data["legitimate_count"] >= 0


def test_reports_returns_list():
    response = client.get("/reports")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
