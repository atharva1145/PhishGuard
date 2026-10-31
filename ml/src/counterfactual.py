"""
PhishGuard Counterfactual Explainability Simulation Engine
Allows interactive 'What-If' simulations by modifying structural features
and calculating the mathematical effect on the model's prediction probability.
"""

from __future__ import annotations
import copy
from typing import Dict, Any, List, Optional
import numpy as np

from ml.src.url_features import extract_url_features, FEATURE_NAMES
from ml.src.predict import get_url_model_pkg


def simulate_counterfactual_url(
    original_url: str,
    modifications: Dict[str, bool]
) -> Dict[str, Any]:
    """
    Applies counterfactual modifications to the URL feature vector and runs real-time
    model inference using the trained Logistic Regression and Scaler pipeline.

    Supported modification toggles:
        - force_https: bool (Set HTTPS scheme)
        - clean_hostname: bool (Remove raw IP, punycode, hyphens in host, excessive digits)
        - remove_subdomains: bool (Set subdomains to 0, reset hostname dot count)
        - standard_tld: bool (Replace abusive TLD like .xyz/.top with standard .com)
        - standard_port: bool (Remove non-standard ports like :8080)
        - strip_sensitive_path: bool (Remove login/verify keywords, query strings, @ symbols)
    """
    pkg = get_url_model_pkg()
    scaler = pkg["scaler"]
    classifier = pkg["classifier"]

    # 1. Extract base feature vector
    base_features = extract_url_features(original_url)
    base_vec = np.array([base_features[name] for name in FEATURE_NAMES])
    base_scaled = scaler.transform(base_vec.reshape(1, -1))
    orig_proba = float(classifier.predict_proba(base_scaled)[0, 1])
    orig_is_phish = orig_proba >= 0.5

    # 2. Clone and apply modifications
    sim_features = copy.deepcopy(base_features)
    remediated_factors: List[str] = []

    if modifications.get("force_https"):
        if sim_features["is_https"] == 0.0:
            sim_features["is_https"] = 1.0
            remediated_factors.append("Enforced secure TLS encryption (HTTPS)")

    if modifications.get("clean_hostname"):
        sim_features["has_ip_address"] = 0.0
        sim_features["has_punycode"] = 0.0
        sim_features["has_prefix_suffix_in_host"] = 0.0
        sim_features["num_hyphens_hostname"] = 0.0
        sim_features["num_digits_hostname"] = 0.0
        sim_features["hostname_length"] = min(sim_features["hostname_length"], 15.0)
        remediated_factors.append("Replaced lookalike host with standard alphanumeric domain")

    if modifications.get("remove_subdomains"):
        if sim_features["num_subdomains"] > 0.0:
            sim_features["num_subdomains"] = 0.0
            sim_features["num_dots_hostname"] = 1.0
            sim_features["num_dots"] = max(1.0, sim_features["num_dots"] - 2.0)
            remediated_factors.append("Removed multi-level subdomain stacking")

    if modifications.get("standard_tld"):
        if sim_features["has_suspicious_tld"] == 1.0:
            sim_features["has_suspicious_tld"] = 0.0
            remediated_factors.append("Replaced high-abuse TLD with standard reputable TLD (.com)")

    if modifications.get("standard_port"):
        if sim_features["has_suspicious_port"] == 1.0:
            sim_features["has_suspicious_port"] = 0.0
            remediated_factors.append("Removed non-standard connection port")

    if modifications.get("strip_sensitive_path"):
        sim_features["num_sensitive_keywords"] = 0.0
        sim_features["has_at_symbol"] = 0.0
        sim_features["num_percent_encoded"] = 0.0
        sim_features["path_length"] = min(sim_features["path_length"], 12.0)
        sim_features["query_length"] = 0.0
        sim_features["num_special_chars"] = max(0.0, sim_features["num_special_chars"] - 3.0)
        remediated_factors.append("Stripped credential harvesting keywords & query tokens")

    # Adjust overall URL length based on path & host modifications
    sim_features["url_length"] = (
        sim_features["hostname_length"] + 
        sim_features["path_length"] + 
        sim_features["query_length"] + 8.0
    )

    # 3. Recalculate inference on counterfactual vector
    sim_vec = np.array([sim_features[name] for name in FEATURE_NAMES])
    sim_scaled = scaler.transform(sim_vec.reshape(1, -1))
    sim_proba = float(classifier.predict_proba(sim_scaled)[0, 1])
    sim_is_phish = sim_proba >= 0.5

    delta = round(sim_proba - orig_proba, 4)
    percent_reduction = round((orig_proba - sim_proba) * 100, 1)

    # Risk level categorization
    if sim_proba >= 0.75:
        sim_risk_level = "High"
    elif sim_proba >= 0.45:
        sim_risk_level = "Medium"
    else:
        sim_risk_level = "Low"

    # Counterfactual conclusion
    verdict_flipped = (orig_is_phish and not sim_is_phish) or (not orig_is_phish and sim_is_phish)

    if verdict_flipped and not sim_is_phish:
        narrative = (
            f"🎉 VERDICT FLIPPED TO LEGITIMATE! Remediating the selected features reduced phishing probability "
            f"from {round(orig_proba * 100, 1)}% down to {round(sim_proba * 100, 1)}% (Δ {round(delta * 100, 1)}%)."
        )
    elif orig_is_phish and sim_proba < orig_proba:
        narrative = (
            f"Risk significantly reduced by {percent_reduction}%, shifting probability to {round(sim_proba * 100, 1)}%. "
            f"The remaining risk is driven by residual lexical length and structural properties."
        )
    else:
        narrative = f"Counterfactual probability: {round(sim_proba * 100, 1)}% (baseline: {round(orig_proba * 100, 1)}%)."

    return {
        "original_url": original_url,
        "original_probability": round(orig_proba, 4),
        "original_prediction": "Potentially Phishing" if orig_is_phish else "Potentially Legitimate",
        "counterfactual_probability": round(sim_proba, 4),
        "counterfactual_prediction": "Potentially Phishing" if sim_is_phish else "Potentially Legitimate",
        "probability_delta": delta,
        "percent_reduction": percent_reduction,
        "counterfactual_risk_level": sim_risk_level,
        "verdict_flipped": verdict_flipped,
        "remediated_factors": remediated_factors,
        "narrative": narrative,
        "applied_modifications": modifications,
    }
