"""
Automated Unit Tests for Email NLP Preprocessing & Risk Indicators
"""

import pytest
from ml.src.email_pipeline import (
    clean_and_normalize_text,
    combine_subject_and_body,
    extract_email_risk_indicators,
    build_email_pipeline
)


def test_text_cleaning_and_entity_replacement():
    """Verify HTML stripping, entity tokens, and whitespace cleanup."""
    raw = "<p>Urgent: Click here to verify https://example.com/login and send $500 to test@paypal.com</p>"
    cleaned = clean_and_normalize_text(raw)
    
    assert "<p>" not in cleaned
    assert "</p>" not in cleaned
    assert "__url__" in cleaned
    assert "__money__" in cleaned
    assert "__email__" in cleaned


def test_combine_subject_and_body():
    """Ensure subject and body are formatted properly."""
    combined = combine_subject_and_body("Account Alert", "Your account was compromised.")
    assert "subject: account alert" in combined
    assert "body: your account was compromised" in combined


def test_email_risk_indicators():
    """Verify detection of urgency, credential requests, and payment patterns."""
    subj = "URGENT: Your account suspended within 24 hours"
    body = "Please verify your password immediately and complete wire transfer to unlock."
    
    indicators = extract_email_risk_indicators(subj, body)
    ind_ids = [i["id"] for i in indicators]
    
    assert "URGENCY_PRESSURE" in ind_ids
    assert "CREDENTIAL_HARVESTING" in ind_ids
    assert "FINANCIAL_FRAUD_THEME" in ind_ids


def test_pipeline_construction():
    """Verify scikit-learn pipeline steps and parameters."""
    pipeline = build_email_pipeline()
    assert "tfidf" in pipeline.named_steps
    assert "classifier" in pipeline.named_steps
