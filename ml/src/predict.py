"""
PhishGuard Prediction & Inference Engine
Loads persisted pipelines and applies real-time inference, risk indicator extraction,
and feature explanation.
"""

from __future__ import annotations
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import joblib
import numpy as np

from ml.src.url_features import (
    extract_url_features, 
    extract_url_risk_indicators, 
    tokenize_url_structure,
    FEATURE_NAMES
)
from ml.src.typosquatting import detect_brand_impersonation
from ml.src.email_pipeline import combine_subject_and_body, extract_email_risk_indicators
from ml.src.explain import explain_url_prediction, explain_email_prediction

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
URL_MODEL_PATH = MODELS_DIR / "url_detector.joblib"
EMAIL_MODEL_PATH = MODELS_DIR / "email_detector.joblib"

_cached_url_pkg: Optional[Dict[str, Any]] = None
_cached_email_pkg: Optional[Dict[str, Any]] = None


def get_url_model_pkg() -> Dict[str, Any]:
    """Lazy loader for URL model artifact."""
    global _cached_url_pkg
    if _cached_url_pkg is None:
        if not URL_MODEL_PATH.exists():
            raise FileNotFoundError(f"URL model artifact not found at {URL_MODEL_PATH}. Run training pipeline first.")
        _cached_url_pkg = joblib.load(URL_MODEL_PATH)
    return _cached_url_pkg


def get_email_model_pkg() -> Dict[str, Any]:
    """Lazy loader for Email model artifact."""
    global _cached_email_pkg
    if _cached_email_pkg is None:
        if not EMAIL_MODEL_PATH.exists():
            raise FileNotFoundError(f"Email model artifact not found at {EMAIL_MODEL_PATH}. Run training pipeline first.")
        _cached_email_pkg = joblib.load(EMAIL_MODEL_PATH)
    return _cached_email_pkg


def predict_url(url_str: str) -> Dict[str, Any]:
    """
    Analyzes URL using the trained URL classifier, feature extractor, and XAI engine.
    """
    pkg = get_url_model_pkg()
    scaler = pkg["scaler"]
    classifier = pkg["classifier"]
    version = pkg.get("model_version", "v1.0.0")

    # Extract numerical features
    features = extract_url_features(url_str)
    feat_vec = np.array([features[name] for name in FEATURE_NAMES])
    scaled_vec = scaler.transform(feat_vec.reshape(1, -1))

    # Inference
    proba_phish = float(classifier.predict_proba(scaled_vec)[0, 1])
    is_phishing = proba_phish >= 0.5
    label = "Potentially Phishing" if is_phishing else "Potentially Legitimate"

    # Risk level categorization
    if proba_phish >= 0.75:
        risk_level = "High"
    elif proba_phish >= 0.45:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # Risk indicators (rule-based heuristic signals)
    indicators = extract_url_risk_indicators(url_str)

    # Brand Impersonation / Typosquatting Check
    brand_impersonation = detect_brand_impersonation(url_str)
    if brand_impersonation:
        indicators.insert(0, {
            "id": "BRAND_IMPERSONATION_DETECTED",
            "name": f"Brand Impersonation: {brand_impersonation['target_brand']}",
            "severity": "HIGH",
            "description": brand_impersonation["details"],
            "evidence": f"Technique: {brand_impersonation['spoof_technique']} (Target: {brand_impersonation['canonical_domain']})",
            "rationale": "Phishers systematically craft lookalike domains (typosquatting, homoglyphs, or subdomain stacking) to impersonate trusted institutions."
        })

    # Multi-Model Consensus (Logistic Regression vs Random Forest)
    rf_clf = pkg.get("rf_classifier")
    models_eval = [
        {
            "model_name": "Logistic Regression (Primary XAI)",
            "prediction": label,
            "phishing_probability": round(proba_phish, 4),
            "is_phishing": is_phishing
        }
    ]
    if rf_clf is not None:
        rf_proba = float(rf_clf.predict_proba(scaled_vec)[0, 1])
        rf_phish = rf_proba >= 0.5
        models_eval.append({
            "model_name": "Random Forest (Secondary)",
            "prediction": "Potentially Phishing" if rf_phish else "Potentially Legitimate",
            "phishing_probability": round(rf_proba, 4),
            "is_phishing": rf_phish
        })
        agree_count = sum(1 for m in models_eval if m["is_phishing"] == is_phishing)
        consensus_verdict = f"{agree_count}/2 Models Agree ({label})" if agree_count == 2 else "Split Decision (Model Divergence)"
        ensemble_consensus = {
            "models_evaluated": 2,
            "consensus_verdict": consensus_verdict,
            "agreement_ratio": round(agree_count / 2, 2),
            "models": models_eval
        }
    else:
        ensemble_consensus = {
            "models_evaluated": 1,
            "consensus_verdict": "Single Model Evaluation",
            "agreement_ratio": 1.0,
            "models": models_eval
        }

    # Feature contributions (log-odds XAI)
    contributions = explain_url_prediction(
        feature_dict=features,
        feature_vector=feat_vec,
        scaler=scaler,
        classifier=classifier,
        feature_names=FEATURE_NAMES,
        top_k=6
    )

    # Human-readable summary
    if is_phishing:
        key_reasons = [c["display_name"] for c in contributions if c["direction"] == "phishing"][:3]
        if key_reasons:
            explanation = (
                f"Classified as Potentially Phishing ({round(proba_phish * 100, 1)}% probability). "
                f"The highest contributing factors are: {', '.join(key_reasons)}."
            )
        else:
            explanation = f"Classified as Potentially Phishing based on structural characteristics ({round(proba_phish * 100, 1)}% confidence)."
    else:
        explanation = (
            f"Classified as Potentially Legitimate ({round((1 - proba_phish) * 100, 1)}% confidence). "
            f"Structure conforms to standard legitimate web hosts with low risk indicators."
        )

    return {
        "target": url_str,
        "scan_type": "url",
        "prediction": label,
        "is_phishing": is_phishing,
        "confidence_score": round(proba_phish if is_phishing else (1.0 - proba_phish), 4),
        "phishing_probability": round(proba_phish, 4),
        "risk_level": risk_level,
        "risk_indicators": indicators,
        "brand_impersonation": brand_impersonation,
        "ensemble_consensus": ensemble_consensus,
        "feature_contributions": contributions,
        "syntax_tokens": tokenize_url_structure(url_str),
        "features": features,
        "explanation": explanation,
        "model_version": version,
        "timestamp": datetime.now().isoformat(),
        "disclaimer": "Predictions are probabilistic and based purely on lexical string characteristics. PhishGuard does not execute or visit the URL."
    }


def predict_email(subject: str, body: str) -> Dict[str, Any]:
    """
    Analyzes email subject and body using the trained NLP pipeline and XAI engine.
    """
    pkg = get_email_model_pkg()
    pipeline = pkg["pipeline"]
    version = pkg.get("model_version", "v1.0.0")

    combined_text = combine_subject_and_body(subject, body)
    
    # Inference
    proba_phish = float(pipeline.predict_proba([combined_text])[0, 1])
    is_phishing = proba_phish >= 0.5
    label = "Potentially Phishing" if is_phishing else "Potentially Legitimate"

    if proba_phish >= 0.75:
        risk_level = "High"
    elif proba_phish >= 0.45:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # Heuristic NLP indicators
    indicators = extract_email_risk_indicators(subject, body)

    # Influential terms from TF-IDF + Classifier
    influential_terms = explain_email_prediction(combined_text, pipeline, top_k=8)

    # Synthesis explanation
    if is_phishing:
        key_words = [t["term"] for t in influential_terms if t["direction"] == "phishing"][:4]
        if key_words:
            explanation = (
                f"Classified as Potentially Phishing ({round(proba_phish * 100, 1)}% probability). "
                f"High-weight vocabulary detected: '{', '.join(key_words)}'."
            )
        else:
            explanation = f"Classified as Potentially Phishing based on linguistic social engineering patterns ({round(proba_phish * 100, 1)}% confidence)."
    else:
        explanation = (
            f"Classified as Potentially Legitimate ({round((1 - proba_phish) * 100, 1)}% confidence). "
            f"Message exhibits standard collaborative or conversational language without high-urgency threats."
        )

    return {
        "target_preview": f"Subject: {subject[:60]}..." if len(subject) > 60 else f"Subject: {subject}",
        "scan_type": "email",
        "prediction": label,
        "is_phishing": is_phishing,
        "confidence_score": round(proba_phish if is_phishing else (1.0 - proba_phish), 4),
        "phishing_probability": round(proba_phish, 4),
        "risk_level": risk_level,
        "risk_indicators": indicators,
        "influential_terms": influential_terms,
        "explanation": explanation,
        "model_version": version,
        "timestamp": datetime.now().isoformat(),
        "warning": (
            "Benign messages can contain suspicious vocabulary (e.g. billing notifications), "
            "and sophisticated phishing campaigns can appear authentic. "
            "PhishGuard analyzes textual content only and does NOT verify email headers, SPF, DKIM, or DMARC."
        )
    }
