"""
PhishGuard Model & Metrics Service
Provides model readiness checks, metadata inspection, and report loading.
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from backend.app.core.config import MODELS_DIR, REPORTS_DIR

logger = logging.getLogger(__name__)


def check_models_health() -> Dict[str, Any]:
    """Checks if model files and reports exist on disk."""
    url_model_path = MODELS_DIR / "url_detector.joblib"
    email_model_path = MODELS_DIR / "email_detector.joblib"

    url_ready = url_model_path.exists()
    email_ready = email_model_path.exists()

    return {
        "url_classifier": {
            "ready": url_ready,
            "path": str(url_model_path),
            "size_bytes": url_model_path.stat().st_size if url_ready else 0
        },
        "email_classifier": {
            "ready": email_ready,
            "path": str(email_model_path),
            "size_bytes": email_model_path.stat().st_size if email_ready else 0
        },
        "all_ready": url_ready and email_ready
    }


def get_model_metadata() -> Dict[str, Any]:
    """Loads metadata from ml/models/metadata.json."""
    meta_path = MODELS_DIR / "metadata.json"
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading metadata.json: {e}")

    # Fallback default metadata if file is missing
    return {
        "pipeline_version": "1.0.0",
        "last_trained_at": None,
        "models": {
            "url_detector": {"status": "uninitialized"},
            "email_detector": {"status": "uninitialized"}
        }
    }


def load_evaluation_report(filename: str) -> Optional[Dict[str, Any]]:
    """Loads a specific evaluation report from ml/reports/."""
    file_path = REPORTS_DIR / filename
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading report {filename}: {e}")
    return None
