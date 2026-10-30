"""
PhishGuard URL Scanning Service
Executes model prediction and logs sanitized metadata to history.
"""

from __future__ import annotations
import uuid
from typing import Dict, Any
from ml.src.predict import predict_url
from backend.app.database.db import insert_scan_record


def execute_url_scan(url_str: str) -> Dict[str, Any]:
    """
    Executes URL prediction and logs to history.
    Never fetches content from the internet.
    """
    prediction_result = predict_url(url_str)
    scan_id = str(uuid.uuid4())

    # Build DB history record (sanitized preview)
    target_preview = url_str[:100] + ("..." if len(url_str) > 100 else "")
    db_record = {
        "scan_id": scan_id,
        "scan_type": "url",
        "target_preview": target_preview,
        "prediction": prediction_result["prediction"],
        "is_phishing": prediction_result["is_phishing"],
        "confidence_score": prediction_result["confidence_score"],
        "risk_level": prediction_result["risk_level"],
        "indicators_count": len(prediction_result["risk_indicators"]),
        "model_version": prediction_result["model_version"],
        "created_at": prediction_result["timestamp"],
        "details": {
            "risk_indicators": prediction_result["risk_indicators"],
            "feature_contributions": prediction_result["feature_contributions"],
            "explanation": prediction_result["explanation"],
            "phishing_probability": prediction_result["phishing_probability"]
        }
    }
    insert_scan_record(db_record)

    # Return full response
    return {
        "scan_id": scan_id,
        **prediction_result
    }
