"""
PhishGuard URL Scanning Service
Executes model prediction and logs sanitized metadata to history.
"""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Dict, Any, List
from ml.src.predict import predict_url
from ml.src.defang import defang_url
from backend.app.database.db import insert_scan_record


def execute_url_scan(url_str: str) -> Dict[str, Any]:
    """
    Executes URL prediction and logs to history.
    Never fetches content from the internet.
    """
    prediction_result = predict_url(url_str)
    scan_id = str(uuid.uuid4())
    defanged_target = defang_url(url_str)

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
            "phishing_probability": prediction_result["phishing_probability"],
            "defanged_target": defanged_target
        }
    }
    insert_scan_record(db_record)

    # Return full response
    return {
        "scan_id": scan_id,
        "defanged_target": defanged_target,
        **prediction_result
    }


def execute_batch_url_scan(urls: List[str]) -> Dict[str, Any]:
    """
    Executes batch threat triage for up to 100 URLs in parallel local analysis.
    """
    cleaned_urls = [u.strip() for u in urls if u and u.strip()]
    seen = set()
    unique_urls = []
    for u in cleaned_urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    results = []
    high_count = 0
    med_count = 0
    low_count = 0
    phish_count = 0

    for u in unique_urls[:100]:
        try:
            scan_res = predict_url(u)
            scan_id = str(uuid.uuid4())
            defanged = defang_url(u)

            if scan_res["risk_level"] == "High":
                high_count += 1
            elif scan_res["risk_level"] == "Medium":
                med_count += 1
            else:
                low_count += 1

            if scan_res["is_phishing"]:
                phish_count += 1

            brand = scan_res.get("brand_impersonation", {}).get("target_brand") if scan_res.get("brand_impersonation") else None
            top_ind = scan_res["risk_indicators"][0]["name"] if scan_res.get("risk_indicators") else None

            results.append({
                "scan_id": scan_id,
                "target": u,
                "defanged_target": defanged,
                "prediction": scan_res["prediction"],
                "is_phishing": scan_res["is_phishing"],
                "confidence_score": scan_res["confidence_score"],
                "phishing_probability": scan_res["phishing_probability"],
                "risk_level": scan_res["risk_level"],
                "target_brand": brand,
                "top_indicator": top_ind
            })
        except Exception:
            continue

    total = len(results)
    summary = {
        "total": total,
        "high_risk": high_count,
        "medium_risk": med_count,
        "low_risk": low_count,
        "phishing_count": phish_count,
        "legitimate_count": total - phish_count
    }

    return {
        "summary": summary,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }
