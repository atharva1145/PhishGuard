"""
Automated Backend API Tests
Tests health, model metadata, URL scanning, email scanning, validation, and error responses.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify root documentation link and service status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "PhishGuard" in data["name"]


def test_health_endpoint():
    """Verify health endpoint reports healthy and model readiness."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "models_ready" in data
    assert "database_status" in data


def test_models_metadata_endpoint():
    """Verify model registry returns metadata."""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "pipeline_version" in data
    assert "models" in data


def test_scan_url_valid_phishing():
    """Verify scanning a suspicious URL returns structured prediction and indicators."""
    payload = {"url": "http://192.168.1.1:8080/paypal/login.php"}
    response = client.post("/api/scan/url", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert data["scan_type"] == "url"
    assert data["is_phishing"] is True
    assert data["prediction"] == "Potentially Phishing"
    assert len(data["risk_indicators"]) > 0
    assert len(data["feature_contributions"]) > 0
    assert "explanation" in data


def test_scan_url_valid_legitimate():
    """Verify scanning an official legitimate URL."""
    payload = {"url": "https://www.google.com/search?q=cybersecurity"}
    response = client.post("/api/scan/url", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == "Potentially Legitimate"
    assert data["is_phishing"] is False


def test_scan_url_invalid_length():
    """Verify URL rejection if too short or too long."""
    # Too short
    resp_short = client.post("/api/scan/url", json={"url": "a"})
    assert resp_short.status_code == 422

    # Too long (> 2048 characters)
    resp_long = client.post("/api/scan/url", json={"url": "http://example.com/" + "x" * 2050})
    assert resp_long.status_code == 422


def test_scan_email_valid_phishing():
    """Verify scanning an urgent phishing email."""
    payload = {
        "subject": "URGENT: Your account suspended within 24 hours",
        "body": "Please click the link below immediately and verify your password to prevent termination."
    }
    response = client.post("/api/scan/email", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert data["scan_type"] == "email"
    assert data["is_phishing"] is True
    assert len(data["influential_terms"]) > 0
    assert "warning" in data


def test_scan_email_valid_legitimate():
    """Verify scanning a legitimate business message."""
    payload = {
        "subject": "Weekly Engineering Sync Agenda",
        "body": "Hi team, please find attached the agenda for our sprint planning session tomorrow at 10 AM."
    }
    response = client.post("/api/scan/email", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == "Potentially Legitimate"
    assert data["is_phishing"] is False


def test_scan_email_empty_body():
    """Verify email body validation fails on empty input."""
    response = client.post("/api/scan/email", json={"subject": "Hi", "body": "   "})
    assert response.status_code == 422


def test_metrics_endpoint():
    """Verify metrics endpoint returns evaluation reports and scan stats."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "url_evaluation" in data
    assert "email_evaluation" in data
    assert "scan_statistics" in data


def test_scan_email_file_upload_valid():
    """Verify uploading and analyzing a valid .eml MIME file."""
    import io
    
    eml_content = (
        "From: security-alert@paypal.com.fake\r\n"
        "To: victim@example.com\r\n"
        "Subject: URGENT: Your PayPal Account Suspended\r\n"
        "Date: Thu, 29 Oct 2026 00:00:00 +0000\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        "\r\n"
        "Please click http://paypal-verify.xyz/login immediately to confirm your password.\r\n"
    ).encode("utf-8")

    file_obj = io.BytesIO(eml_content)
    response = client.post(
        "/api/scan/email/file",
        files={"file": ("suspicious_alert.eml", file_obj, "message/rfc822")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["scan_type"] == "email"
    assert data["is_phishing"] is True
    assert "eml_metadata" in data
    assert data["eml_metadata"]["from_header"] == "security-alert@paypal.com.fake"
    assert len(data["eml_metadata"]["embedded_urls"]) > 0


def test_scan_email_file_upload_invalid_extension():
    """Verify rejecting invalid file formats like .exe or .pdf."""
    import io
    response = client.post(
        "/api/scan/email/file",
        files={"file": ("payload.exe", io.BytesIO(b"MZ..."), "application/octet-stream")}
    )
    assert response.status_code == 400
