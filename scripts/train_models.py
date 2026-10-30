"""
PhishGuard Model Training Runner Script
Trains URL and Email phishing classifiers, performs cross-validation comparisons,
generates strict evaluation reports, and serializes trained models.
"""

from __future__ import annotations
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.src.train_url_model import train_and_evaluate_url_models
from ml.src.train_email_model import train_and_evaluate_email_models

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("phishguard_train")


def main():
    logger.info("=" * 60)
    logger.info("Starting PhishGuard ML Model Training & Evaluation Pipeline")
    logger.info("=" * 60)

    # 1. URL Model Training & Evaluation
    logger.info("--> [1/2] Training URL Phishing Detector...")
    url_report = train_and_evaluate_url_models()
    logger.info(
        f"URL Model training complete. Test Accuracy: {url_report['metrics']['accuracy'] * 100:.2f}%, "
        f"F1: {url_report['metrics']['f1_score']:.4f}, FPR: {url_report['metrics']['false_positive_rate']}"
    )

    # 2. Email Model Training & Evaluation
    logger.info("--> [2/2] Training Email Phishing Detector...")
    email_report = train_and_evaluate_email_models()
    logger.info(
        f"Email Model training complete. Test Accuracy: {email_report['metrics']['accuracy'] * 100:.2f}%, "
        f"F1: {email_report['metrics']['f1_score']:.4f}, FPR: {email_report['metrics']['false_positive_rate']}"
    )

    # 3. Model Comparison Summary
    reports_dir = PROJECT_ROOT / "ml" / "reports"
    models_dir = PROJECT_ROOT / "ml" / "models"
    
    combined_comparison = {
        "generated_at": datetime.now().isoformat(),
        "url_classifier": {
            "selected_model": url_report["algorithm"],
            "version": url_report["model_version"],
            "metrics": url_report["metrics"],
            "candidates_cv": url_report["model_comparison"]
        },
        "email_classifier": {
            "selected_model": email_report["algorithm"],
            "version": email_report["model_version"],
            "metrics": email_report["metrics"],
            "candidates_cv": email_report["model_comparison"]
        }
    }
    
    comparison_path = reports_dir / "model_comparison.json"
    with open(comparison_path, "w", encoding="utf-8") as f:
        json.dump(combined_comparison, f, indent=2)
    logger.info(f"Model comparison summary written to {comparison_path}")

    # Metadata file
    metadata = {
        "pipeline_version": "1.0.0",
        "last_trained_at": datetime.now().isoformat(),
        "models": {
            "url_detector": {
                "file": "url_detector.joblib",
                "version": url_report["model_version"],
                "algorithm": url_report["algorithm"],
                "features_count": url_report["feature_count"],
                "test_accuracy": url_report["metrics"]["accuracy"],
                "test_f1": url_report["metrics"]["f1_score"]
            },
            "email_detector": {
                "file": "email_detector.joblib",
                "version": email_report["model_version"],
                "algorithm": email_report["algorithm"],
                "vocabulary_size": email_report["vocabulary_size"],
                "test_accuracy": email_report["metrics"]["accuracy"],
                "test_f1": email_report["metrics"]["f1_score"]
            }
        }
    }

    metadata_path = models_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Metadata file written to {metadata_path}")

    logger.info("=" * 60)
    logger.info("All PhishGuard models successfully trained, evaluated, and saved!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
