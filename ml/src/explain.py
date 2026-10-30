"""
PhishGuard Explainable AI (XAI) Engine
Provides transparent feature attributions for linear models, coefficient analysis,
influential term extraction, and deterministic heuristic synthesis.

Never fabricates explanations. When an attribution cannot be established mathematically,
clearly states that it is unavailable.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import numpy as np


# Human-friendly descriptions and display titles for URL features
URL_FEATURE_METADATA = {
    "url_length": ("Total URL Length", "Long URLs often hide malicious targets or tracking sequences."),
    "hostname_length": ("Hostname Length", "Unusually long hostnames are common in domain spoofing."),
    "path_length": ("Path Length", "Deep nested paths conceal attack payload endpoints."),
    "query_length": ("Query String Length", "Extensive parameters often carry encoded payloads or redirects."),
    "num_dots": ("Total Dots", "Excessive dots indicate nested domains or obfuscated file extensions."),
    "num_dots_hostname": ("Dots in Hostname", "Indicates multiple subdomains or spoofed domains."),
    "num_subdomains": ("Subdomain Count", "Attackers stack trusted brand names as subdomains."),
    "num_hyphens": ("Total Hyphens", "Hyphens are heavily used in impersonated brand names."),
    "num_hyphens_hostname": ("Hyphens in Hostname", "Combines brand keywords e.g. 'paypal-support'."),
    "num_digits": ("Total Digits", "Random hex or numeric IDs in attack landing pages."),
    "num_digits_hostname": ("Digits in Hostname", "Legitimate brand hostnames rarely include high digit counts."),
    "digit_ratio": ("Digit-to-Character Ratio", "High numeric ratios correlate with disposable hosts."),
    "num_special_chars": ("Special Characters Count", "Unusual symbols used for obfuscation and query manipulation."),
    "has_ip_address": ("Raw IP Address Host", "Bypasses standard DNS registration and domain blocklists."),
    "has_punycode": ("Punycode Homograph", "Internationalized characters visually spoofing legitimate letters."),
    "is_https": ("HTTPS Encryption", "Encrypted transmission protocol (note: phishers also use HTTPS)."),
    "has_at_symbol": ("Embedded '@' Symbol", "Obscures the true destination host in URL userinfo syntax."),
    "has_suspicious_port": ("Non-Standard Web Port", "Web services hosted on non-standard ports like 8080/8888."),
    "num_percent_encoded": ("Percent Encoded Characters", "URL encoding used to evade basic keyword filters."),
    "has_shortener": ("URL Shortener Service", "Hides destination host and circumvents preliminary reputation lookups."),
    "has_suspicious_tld": ("High-Abuse TLD", "Top-level domain frequently associated with spam and phishing campaigns."),
    "num_sensitive_keywords": ("Target Authentication Keywords", "Presence of keywords like login, verify, secure, banking."),
    "has_prefix_suffix_in_host": ("Hyphenated Brand Prefix/Suffix", "Brand impersonation through hyphens in domain."),
    "is_valid_url": ("Valid URL Structure", "Basic RFC-compliant URL formatting."),
}


def explain_url_prediction(
    feature_dict: Dict[str, float],
    feature_vector: np.ndarray,
    scaler,
    classifier,
    feature_names: List[str],
    top_k: int = 6
) -> List[Dict[str, Any]]:
    """
    Computes exact log-odds feature contributions for Logistic Regression:
    Contribution_i = beta_i * (x_i - mean_i) / std_i
    """
    if not hasattr(classifier, "coef_"):
        return []

    coefs = classifier.coef_[0]
    
    # Scale feature vector
    if scaler is not None:
        scaled_vec = scaler.transform(feature_vector.reshape(1, -1))[0]
    else:
        scaled_vec = feature_vector

    contributions = []
    for idx, name in enumerate(feature_names):
        weight = coefs[idx]
        val = scaled_vec[idx]
        contrib = float(weight * val)
        raw_val = feature_dict.get(name, 0.0)

        meta = URL_FEATURE_METADATA.get(name, (name, "Engineered structural URL feature."))

        contributions.append({
            "feature": name,
            "display_name": meta[0],
            "description": meta[1],
            "raw_value": round(float(raw_val), 4) if isinstance(raw_val, float) else raw_val,
            "contribution": round(contrib, 4),
            "direction": "phishing" if contrib > 0 else "legitimate",
            "abs_contribution": abs(contrib),
        })

    # Sort by absolute contribution strength
    contributions.sort(key=lambda x: x["abs_contribution"], reverse=True)
    return contributions[:top_k]


def explain_email_prediction(
    cleaned_text: str,
    pipeline,
    top_k: int = 8
) -> List[Dict[str, Any]]:
    """
    Extracts the most influential TF-IDF terms for the email classification.
    Calculates word contribution = tfidf_weight * logistic_regression_coefficient.
    """
    try:
        tfidf = pipeline.named_steps["tfidf"]
        clf = pipeline.named_steps["classifier"]
    except KeyError:
        return []

    if not hasattr(clf, "coef_"):
        return []

    coefs = clf.coef_[0]
    vec = tfidf.transform([cleaned_text])
    
    # Non-zero indices in input
    non_zero_indices = vec.nonzero()[1]
    if len(non_zero_indices) == 0:
        return []

    feature_names = tfidf.get_feature_names_out()
    influential_terms = []

    for idx in non_zero_indices:
        tfidf_val = vec[0, idx]
        weight = coefs[idx]
        contrib = float(tfidf_val * weight)
        term = feature_names[idx]

        influential_terms.append({
            "term": term,
            "tfidf_value": round(float(tfidf_val), 4),
            "coefficient": round(float(weight), 4),
            "contribution": round(contrib, 4),
            "direction": "phishing" if contrib > 0 else "legitimate",
            "abs_contribution": abs(contrib),
        })

    # Sort by absolute influence
    influential_terms.sort(key=lambda x: x["abs_contribution"], reverse=True)
    return influential_terms[:top_k]
