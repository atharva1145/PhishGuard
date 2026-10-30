"""
PhishGuard URL Model Training & Comparison Pipeline
Trains baseline Logistic Regression, Random Forest, and Linear SVM classifiers.
Applies strict train/test separation, 5-fold cross validation, and exports serialized models & evaluation reports.
"""

from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold, cross_validate

from ml.src.data_loader import load_raw_url_dataset
from ml.src.data_validation import validate_and_clean_url_dataset, split_dataset, verify_split_leakage
from ml.src.url_features import extract_url_features, FEATURE_NAMES
from ml.src.evaluate import calculate_metrics, find_misclassified_examples, export_evaluation_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def extract_features_df(urls: pd.Series) -> pd.DataFrame:
    """Vectorize a pandas Series of URLs into a DataFrame of numerical features."""
    features_list = [extract_url_features(u) for u in urls]
    return pd.DataFrame(features_list)[FEATURE_NAMES]


def train_and_evaluate_url_models() -> Dict[str, Any]:
    """
    Executes the full training, validation, comparison, and evaluation pipeline for URL detection.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load and validate dataset
    raw_df = load_raw_url_dataset()
    clean_df = validate_and_clean_url_dataset(raw_df)

    # 2. Split dataset with leakage prevention
    train_df, test_df = split_dataset(clean_df, test_size=0.2, random_state=42)
    verify_split_leakage(train_df["url"], test_df["url"], name="URLs")

    logger.info(f"URL Dataset split: {len(train_df)} training samples, {len(test_df)} test samples.")

    # 3. Extract features
    X_train_df = extract_features_df(train_df["url"])
    y_train = train_df["label"].values

    X_test_df = extract_features_df(test_df["url"])
    y_test = test_df["label"].values

    # 4. Fit scaler ONLY on training data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_df.values)
    X_test_scaled = scaler.transform(X_test_df.values)

    # 5. Define candidate models
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    candidates = {
        "Logistic Regression (Baseline)": LogisticRegression(
            class_weight="balanced",
            C=1.0,
            max_iter=1000,
            random_state=42,
            solver="lbfgs"
        ),
        "Random Forest Classifier": RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            random_state=42,
            class_weight="balanced"
        ),
        "Linear SVM (Calibrated)": CalibratedClassifierCV(
            LinearSVC(random_state=42, dual=False, max_iter=2000),
            cv=3
        )
    }

    comparison_results = []

    # 6. Cross-validation comparison on training data
    for model_name, clf in candidates.items():
        cv_scores = cross_validate(
            clf,
            X_train_scaled,
            y_train,
            cv=cv,
            scoring=["accuracy", "precision", "recall", "f1"],
            return_train_score=False
        )
        comparison_results.append({
            "model_name": model_name,
            "cv_accuracy": round(float(np.mean(cv_scores["test_accuracy"])), 4),
            "cv_precision": round(float(np.mean(cv_scores["test_precision"])), 4),
            "cv_recall": round(float(np.mean(cv_scores["test_recall"])), 4),
            "cv_f1": round(float(np.mean(cv_scores["test_f1"])), 4),
        })

    logger.info(f"Cross-validation comparison: {comparison_results}")

    # 7. Select primary model: Logistic Regression for linear coefficient explainability
    primary_clf = candidates["Logistic Regression (Baseline)"]
    primary_clf.fit(X_train_scaled, y_train)

    # Also fit RF for secondary metrics comparison
    rf_clf = candidates["Random Forest Classifier"]
    rf_clf.fit(X_train_scaled, y_train)

    # 8. Evaluate on held-out test set
    y_test_pred = primary_clf.predict(X_test_scaled)
    y_test_proba = primary_clf.predict_proba(X_test_scaled)[:, 1]

    metrics = calculate_metrics(y_test, y_test_pred, y_test_proba)

    # RF test metrics for comparison table
    rf_pred = rf_clf.predict(X_test_scaled)
    rf_metrics = calculate_metrics(y_test, rf_pred)

    for item in comparison_results:
        if "Logistic Regression" in item["model_name"]:
            item["test_accuracy"] = metrics["accuracy"]
            item["test_f1"] = metrics["f1_score"]
            item["test_precision"] = metrics["precision"]
            item["test_recall"] = metrics["recall"]
            item["selected"] = True
        else:
            item["test_accuracy"] = rf_metrics["accuracy"]
            item["test_f1"] = rf_metrics["f1_score"]
            item["test_precision"] = rf_metrics["precision"]
            item["test_recall"] = rf_metrics["recall"]
            item["selected"] = False

    # 9. Extract sanitized misclassified test examples
    misclassified = find_misclassified_examples(
        items=test_df["url"].tolist(),
        y_true=y_test,
        y_pred=y_test_pred,
        y_scores=y_test_proba,
        item_type="url",
        limit=8
    )

    # 10. Assemble and save model package
    timestamp_str = datetime.now().isoformat()
    model_version = "v1.0.0-logreg-url"

    model_package = {
        "model_version": model_version,
        "algorithm": "Logistic Regression with L2 Regularization & Feature Scaling",
        "created_at": timestamp_str,
        "feature_names": FEATURE_NAMES,
        "scaler": scaler,
        "classifier": primary_clf,
        "rf_classifier": rf_clf,
    }

    model_path = MODELS_DIR / "url_detector.joblib"
    joblib.dump(model_package, model_path)
    logger.info(f"URL Model artifact persisted to {model_path}")

    # 11. Assemble comprehensive evaluation report
    evaluation_report = {
        "model_type": "url_classifier",
        "model_version": model_version,
        "algorithm": model_package["algorithm"],
        "evaluated_at": timestamp_str,
        "dataset_summary": {
            "total_records": len(clean_df),
            "train_records": len(train_df),
            "test_records": len(test_df),
            "class_distribution": {
                "train_legitimate": int((y_train == 0).sum()),
                "train_phishing": int((y_train == 1).sum()),
                "test_legitimate": int((y_test == 0).sum()),
                "test_phishing": int((y_test == 1).sum()),
            }
        },
        "evaluation_protocol": "Stratified 80/20 train/test split. Fitted scaler and feature parameters strictly on training split. Leakage asserted with zero intersection of URLs.",
        "metrics": metrics,
        "model_comparison": comparison_results,
        "misclassified_samples": misclassified,
        "feature_count": len(FEATURE_NAMES),
    }

    report_path = REPORTS_DIR / "url_evaluation.json"
    export_evaluation_report(evaluation_report, report_path)
    logger.info(f"URL Evaluation report saved to {report_path}")

    return evaluation_report


if __name__ == "__main__":
    train_and_evaluate_url_models()
