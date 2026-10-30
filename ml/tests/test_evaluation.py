"""
Automated Unit Tests for Model Evaluation & Safe Metrics Calculation
"""

import pytest
import numpy as np
from ml.src.evaluate import calculate_metrics, find_misclassified_examples


def test_standard_metrics_calculation():
    """Verify accuracy, precision, recall, f1, fpr, fnr."""
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 1, 0, 1])

    # TN=1, FP=1, FN=1, TP=1
    metrics = calculate_metrics(y_true, y_pred)
    assert metrics["accuracy"] == 0.5
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5
    assert metrics["f1_score"] == 0.5
    assert metrics["false_positive_rate"] == 0.5  # FP/(FP+TN) = 1/2
    assert metrics["false_negative_rate"] == 0.5  # FN/(FN+TP) = 1/2


def test_zero_denominator_fpr():
    """Verify that when FP+TN == 0 (no negative class in ground truth), FPR does not crash."""
    y_true = np.array([1, 1, 1])
    y_pred = np.array([1, 1, 0])
    # No legitimate instances: TN=0, FP=0 -> FP+TN = 0
    metrics = calculate_metrics(y_true, y_pred)
    assert metrics["false_positive_rate"] is None
    assert metrics["false_negative_rate"] is not None


def test_zero_denominator_fnr():
    """Verify that when FN+TP == 0 (no positive class in ground truth), FNR does not crash."""
    y_true = np.array([0, 0, 0])
    y_pred = np.array([0, 1, 0])
    # No phishing instances: FN=0, TP=0 -> FN+TP = 0
    metrics = calculate_metrics(y_true, y_pred)
    assert metrics["false_negative_rate"] is None
    assert metrics["false_positive_rate"] is not None


def test_misclassified_examples_sanitization():
    """Verify sanitized extraction of false positives and false negatives."""
    items = ["https://legit-site.org/very/long/path/with/sensitive/info/that/should/be/truncated" * 3, "https://phish.xyz"]
    y_true = np.array([0, 1])
    y_pred = np.array([1, 0])
    y_scores = np.array([0.9, 0.1])

    errors = find_misclassified_examples(items, y_true, y_pred, y_scores, item_type="url")
    assert len(errors) == 2
    assert errors[0]["error_type"] == "False Positive"
    assert errors[1]["error_type"] == "False Negative"
    assert len(errors[0]["preview"]) <= 125
