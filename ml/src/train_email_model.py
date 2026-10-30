"""
PhishGuard Email NLP Model Training & Comparison Pipeline
Trains TF-IDF vectorizers and compares Logistic Regression, Linear SVM, and Naive Bayes classifiers.
Applies rigorous train/test separation, 5-fold cross validation, and exports serialized pipelines & evaluation reports.
"""

from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_validate

from ml.src.data_loader import load_raw_email_dataset
from ml.src.data_validation import validate_and_clean_email_dataset, split_dataset, verify_split_leakage
from ml.src.email_pipeline import combine_subject_and_body
from ml.src.evaluate import calculate_metrics, find_misclassified_examples, export_evaluation_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def train_and_evaluate_email_models() -> Dict[str, Any]:
    """
    Executes the full training, validation, comparison, and evaluation pipeline for Email phishing detection.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load and validate dataset
    raw_df = load_raw_email_dataset()
    clean_df = validate_and_clean_email_dataset(raw_df)

    # 2. Split dataset with leakage prevention
    train_df, test_df = split_dataset(clean_df, test_size=0.2, random_state=42)
    verify_split_leakage(train_df["body"], test_df["body"], name="Email Bodies")

    logger.info(f"Email Dataset split: {len(train_df)} training samples, {len(test_df)} test samples.")

    # 3. Combine subject and body text
    train_texts = [combine_subject_and_body(s, b) for s, b in zip(train_df["subject"], train_df["body"])]
    test_texts = [combine_subject_and_body(s, b) for s, b in zip(test_df["subject"], test_df["body"])]

    y_train = train_df["label"].values
    y_test = test_df["label"].values

    # 4. Define candidate models
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    candidates = {
        "TF-IDF + Logistic Regression": Pipeline([
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2, sublinear_tf=True, stop_words="english")),
            ("classifier", LogisticRegression(class_weight="balanced", C=1.0, max_iter=1000, random_state=42, solver="liblinear"))
        ]),
        "TF-IDF + Linear SVM (SGD)": Pipeline([
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2, sublinear_tf=True, stop_words="english")),
            ("classifier", SGDClassifier(loss="log_loss", penalty="l2", alpha=1e-4, random_state=42, class_weight="balanced"))
        ]),
        "TF-IDF + Multinomial Naive Bayes": Pipeline([
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2, sublinear_tf=True, stop_words="english")),
            ("classifier", MultinomialNB(alpha=0.5))
        ])
    }

    comparison_results = []

    # 5. Cross-validation comparison on training data
    for model_name, pipeline in candidates.items():
        cv_scores = cross_validate(
            pipeline,
            train_texts,
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

    logger.info(f"Email Model comparison: {comparison_results}")

    # 6. Fit primary model (TF-IDF + Logistic Regression) on entire train split
    primary_pipeline = candidates["TF-IDF + Logistic Regression"]
    primary_pipeline.fit(train_texts, y_train)

    # Also fit SVM for test comparison
    svm_pipeline = candidates["TF-IDF + Linear SVM (SGD)"]
    svm_pipeline.fit(train_texts, y_train)

    # 7. Evaluate on held-out test set
    y_test_pred = primary_pipeline.predict(test_texts)
    y_test_proba = primary_pipeline.predict_proba(test_texts)[:, 1]

    metrics = calculate_metrics(y_test, y_test_pred, y_test_proba)

    # SVM test metrics
    svm_pred = svm_pipeline.predict(test_texts)
    svm_metrics = calculate_metrics(y_test, svm_pred)

    for item in comparison_results:
        if "Logistic Regression" in item["model_name"]:
            item["test_accuracy"] = metrics["accuracy"]
            item["test_f1"] = metrics["f1_score"]
            item["test_precision"] = metrics["precision"]
            item["test_recall"] = metrics["recall"]
            item["selected"] = True
        else:
            item["test_accuracy"] = svm_metrics["accuracy"]
            item["test_f1"] = svm_metrics["f1_score"]
            item["test_precision"] = svm_metrics["precision"]
            item["test_recall"] = svm_metrics["recall"]
            item["selected"] = False

    # 8. Extract sanitized misclassified test examples
    sample_previews = [f"Subj: {s} | {b}" for s, b in zip(test_df["subject"], test_df["body"])]
    misclassified = find_misclassified_examples(
        items=sample_previews,
        y_true=y_test,
        y_pred=y_test_pred,
        y_scores=y_test_proba,
        item_type="email",
        limit=8
    )

    # 9. Assemble and save model package
    timestamp_str = datetime.now().isoformat()
    model_version = "v1.0.0-tfidf-logreg-email"

    model_package = {
        "model_version": model_version,
        "algorithm": "TF-IDF N-Gram Vectorizer (1-2) with Logistic Regression",
        "created_at": timestamp_str,
        "pipeline": primary_pipeline,
    }

    model_path = MODELS_DIR / "email_detector.joblib"
    joblib.dump(model_package, model_path)
    logger.info(f"Email Model artifact persisted to {model_path}")

    # 10. Assemble comprehensive evaluation report
    evaluation_report = {
        "model_type": "email_classifier",
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
        "evaluation_protocol": "Stratified 80/20 train/test split. TF-IDF vocabulary fitted exclusively on training split to eliminate data snooping leakage.",
        "metrics": metrics,
        "model_comparison": comparison_results,
        "misclassified_samples": misclassified,
        "vocabulary_size": len(primary_pipeline.named_steps["tfidf"].vocabulary_),
    }

    report_path = REPORTS_DIR / "email_evaluation.json"
    export_evaluation_report(evaluation_report, report_path)
    logger.info(f"Email Evaluation report saved to {report_path}")

    return evaluation_report


if __name__ == "__main__":
    train_and_evaluate_email_models()
