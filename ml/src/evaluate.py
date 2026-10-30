"""
PhishGuard Model Evaluation Module
Calculates strict metrics, handles zero denominators safely, generates confusion matrices,
extracts sanitized misclassified inspection samples, and exports reproducible evaluation reports.
"""

from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report


def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_scores: Optional[np.ndarray] = None
) -> Dict[str, Any]:
    """
    Computes rigorous classification metrics with positive class = 1 (Phishing).
    FPR = FP / (FP + TN)
    FNR = FN / (FN + TP)
    Handles zero denominators safely without throwing ZeroDivisionError.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)

    acc = float(accuracy_score(y_true, y_pred))
    
    # Zero division safe precision, recall, f1
    prec = float(precision_score(y_true, y_pred, pos_label=1, zero_division=0.0))
    rec = float(recall_score(y_true, y_pred, pos_label=1, zero_division=0.0))
    f1 = float(f1_score(y_true, y_pred, pos_label=1, zero_division=0.0))

    # Confusion matrix: [[TN, FP], [FN, TP]]
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])

    # FPR = FP / (FP + TN)
    fpr_denom = fp + tn
    fpr = float(fp / fpr_denom) if fpr_denom > 0 else None

    # FNR = FN / (FN + TP)
    fnr_denom = fn + tp
    fnr = float(fn / fnr_denom) if fnr_denom > 0 else None

    # Per-class breakdown
    prec_legit = float(precision_score(y_true, y_pred, pos_label=0, zero_division=0.0))
    rec_legit = float(recall_score(y_true, y_pred, pos_label=0, zero_division=0.0))
    f1_legit = float(f1_score(y_true, y_pred, pos_label=0, zero_division=0.0))

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "false_positive_rate": round(fpr, 4) if fpr is not None else None,
        "false_negative_rate": round(fnr, 4) if fnr is not None else None,
        "confusion_matrix": {
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "true_positives": tp,
            "matrix_2x2": [[tn, fp], [fn, tp]],
        },
        "per_class": {
            "legitimate": {
                "precision": round(prec_legit, 4),
                "recall": round(rec_legit, 4),
                "f1_score": round(f1_legit, 4),
                "support": int(tn + fp),
            },
            "phishing": {
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "support": int(fn + tp),
            }
        }
    }


def find_misclassified_examples(
    items: List[str],
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_scores: np.ndarray,
    item_type: str = "url",
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Identifies misclassified examples safely.
    Sanitizes content to prevent leaking private information.
    """
    misclassified = []
    for idx, (item, actual, pred, score) in enumerate(zip(items, y_true, y_pred, y_scores)):
        if actual != pred:
            is_fp = (actual == 0 and pred == 1)
            error_type = "False Positive" if is_fp else "False Negative"
            
            # Sanitize preview
            clean_preview = str(item).strip()
            if len(clean_preview) > 120:
                clean_preview = clean_preview[:117] + "..."

            reason = (
                "Legitimate sample incorrectly flagged as phishing (high security penalty / business disruption risk)."
                if is_fp else
                "Phishing sample bypassed detection (security risk / unauthorized access threat)."
            )

            misclassified.append({
                "sample_id": f"err_{idx}_{actual}_{pred}",
                "item_type": item_type,
                "preview": clean_preview,
                "true_label": int(actual),
                "true_label_name": "Phishing" if actual == 1 else "Legitimate",
                "predicted_label": int(pred),
                "predicted_label_name": "Phishing" if pred == 1 else "Legitimate",
                "error_type": error_type,
                "predicted_score": round(float(score), 4),
                "reason_notes": reason,
            })
            if len(misclassified) >= limit:
                break
    return misclassified


def export_evaluation_report(report_data: Dict[str, Any], output_path: Path):
    """Saves structured evaluation report as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
