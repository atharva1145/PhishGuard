"""
Automated Integration Tests for Training Fixture, Deduplication & Leakage Prevention
"""

import pytest
import pandas as pd
from ml.src.data_validation import (
    validate_and_clean_url_dataset,
    validate_and_clean_email_dataset,
    split_dataset,
    verify_split_leakage
)


def test_url_deduplication_and_validation():
    """Ensure duplicate URLs are pruned and invalid labels rejected."""
    raw_df = pd.DataFrame([
        {"url": "https://example.com", "label": 0},
        {"url": "https://example.com", "label": 0},  # duplicate
        {"url": "https://phish.xyz", "label": 1},
        {"url": "invalid", "label": 2},  # invalid label
        {"url": None, "label": 0},
    ])
    cleaned = validate_and_clean_url_dataset(raw_df)
    assert len(cleaned) == 2
    assert set(cleaned["label"].unique()) == {0, 1}


def test_email_deduplication_and_validation():
    """Ensure duplicate emails are removed."""
    raw_df = pd.DataFrame([
        {"subject": "Meeting", "body": "Let us meet tomorrow at 10 AM to discuss the roadmap.", "label": 0},
        {"subject": "Meeting", "body": "Let us meet tomorrow at 10 AM to discuss the roadmap.", "label": 0},
        {"subject": "Alert", "body": "Click here immediately to verify your account or get suspended.", "label": 1},
    ])
    cleaned = validate_and_clean_email_dataset(raw_df)
    assert len(cleaned) == 2


def test_leakage_assertion():
    """Ensure that any overlap between train and test raises an assertion error."""
    train_series = pd.Series(["https://example.com", "https://test.org"])
    test_series = pd.Series(["https://example.com", "https://phish.xyz"])
    
    with pytest.raises(AssertionError):
        verify_split_leakage(train_series, test_series)
